import sys, os

from django.core.exceptions import ObjectDoesNotExist

from ..biofoundry import db
from ..misc import calc, file, parser
from ..container import plate, machine
from db.models import Plate, Well, Sample


# Dispense modo in plate
BY_ROW = 0
BY_COL = 1
MAX_VALUE = 999999


def get_localization_vol(part_name, list_source_wells):
    primer_f, primer_r, template = get_primers_template(part_name, list_source_wells)
    primer_f = 0
    primer_r = 0
    template = 0
    for i, item in enumerate(list_source_wells):
        name, sample_name, sample_direction, sample_type, sample_wellconcentration, available_vol, times_needed, times_available, vol_part_add, sample_platename, sample_wellname, sample_num_well = list_source_wells[i]
        if part_name == name and times_available > 0:
            new_times_available = times_available - 1
            if sample_type == 'Primer':
                if sample_direction == 'FWD':
                    primer_f = list_source_wells[i]
                else:
                    primer_r = list_source_wells[i]
            else:
                template = list_source_wells[i]

            list_source_wells[i] = [
                name, sample_name, sample_direction, sample_type, sample_wellconcentration, available_vol, times_needed,
                new_times_available, vol_part_add, sample_platename, sample_wellname, sample_num_well]

    return list_source_wells, primer_r, primer_f, template


def get_plate_with_empty_well(destination_plates, pattern):
    if pattern == BY_ROW:
        for p in range(0, len(destination_plates)):
            if destination_plates[p].get_empty_well_by_row() is not None:
                i, j = destination_plates[p].get_empty_well_by_row()
                return p, i, j
    else:
        for p in range(0, len(destination_plates)):
            if destination_plates[p].get_empty_well_by_row() is not None:
                i, j = destination_plates[p].get_empty_well_by_col()
                return p, i, j


def populate_destination_plates(plates_out, list_part_count, list_source_wells, mix_parameters, pattern):
    template_conc, conc_primer_f, conc_primer_r, per_buffer, per_phusion, per_dntps, total_vol, add_water = mix_parameters
    alert = []
    out_dispenser = []
    out_master_mix = []
    out_water = []
    for part in list_part_count:
        count = int(part[1])
        for i in range(0, count):
            total_parts_vol = 0
            p, i, j = get_plate_with_empty_well(plates_out, pattern)
            list_source_wells, primer_r, primer_f, template = get_localization_vol(part[0], list_source_wells)
            name_part_pf, pf_name, pf_direction, pf_type, pf_wellconcentration, pf_available_vol, pf_times_needed, pf_times_available, pf_vol_part_add, pf_platename, pf_wellname, pf_num_well = primer_f
            name_part_pr, pr_name, pr_direction, pr_type, pr_wellconcentration, pr_available_vol, pr_times_needed, pr_times_available, pr_vol_part_add, pr_platename, pr_wellname, pr_num_well = primer_r
            name_part_t, t_name, t_direction, t_type, t_wellconcentration, t_available_vol, t_times_needed, t_times_available, t_vol_part_add, t_platename, t_wellname, t_num_well = template

            """ Adding parts in destination plate """
            plates_out[p].wells[i][j].samples.append(plate.Sample(primer_r[1], primer_r[2], primer_r[3], primer_r[4], primer_r[8]))
            plates_out[p].wells[i][j].samples.append(plate.Sample(primer_f[1], primer_f[2], primer_f[3], primer_f[4], primer_f[8]))
            plates_out[p].wells[i][j].samples.append(plate.Sample(template[1], template[2], template[3], template[4], template[8]))
            # header = 'Part', 'Source Plate Name', 'Source Well', 'Destination ID', 'Destination Plate Name', 'Destination Well', 'Volume'
            out_dispenser.append([name_part_pf+'-'+pf_name, pf_type, pf_platename, pf_wellname, pf_vol_part_add, plates_out[p].name, plates_out[p].wells[i][j].name, plates_out[p].id])
            out_dispenser.append([name_part_pr+'-'+pr_name, pr_type, pr_platename, pr_wellname, pr_vol_part_add, plates_out[p].name, plates_out[p].wells[i][j].name, plates_out[p].id])
            out_dispenser.append([name_part_t+'-'+t_name, t_type, t_platename, t_wellname, t_vol_part_add, plates_out[p].name, plates_out[p].wells[i][j].name, plates_out[p].id])

            """ Sum of total volume of parts """
            total_parts_vol += pf_vol_part_add + pr_vol_part_add + t_vol_part_add

            '''Calculate buffer and enzimes'''
            vol_for_mixer = calc_mixer_volumes(mix_parameters)
            phusion_vol, buffer_vol, dNTPS_vol, total_vol_buffer = vol_for_mixer

            '''Total water volume in well'''
            water_vol = total_vol - (total_vol_buffer + total_parts_vol)

            if water_vol >= 0:
                ''' Add receipts in list destination'''
                out_master_mix.append(['buffer', total_vol_buffer, plates_out[p].wells[i][j].name])
                out_water.append(['water', water_vol, plates_out[p].wells[i][j].name])

                ''' Add receipts in destination plate '''
                plates_out[p].wells[i][j].samples.append(plate.Sample('Mastermix_PCR', None, None, None, total_vol_buffer))
                plates_out[p].wells[i][j].samples.append(plate.Sample('Water', None, None, None, water_vol))

            else:
                alert.append('Rx for: ' + str(part[0]) + '. The water volume is negative.')

    return plates_out, out_dispenser, out_master_mix, out_water, alert


def create_plate(num_wells, name):
    rows, cols = calc.rows_columns(int(num_wells))
    new_plate = plate.Plate(rows, cols, name)
    return new_plate


def create_destination_plates(list_part_count, list_destination_plate, out_num_well):
    num = Plate.objects.latest('id').id
    plates_out = []
    num_receipts = 0
    for part in list_part_count:
        num_receipts += int(part[1])

    num_plates = calc.num_destination_plates(num_receipts, out_num_well)

    for i in range(0, num_plates):
        plates_out.append(create_plate(out_num_well, 'PCR_' + '{0:07}'.format(num+1)))
    return plates_out


def create_entry_list_for_destination_plate(list_source_wells, list_part_count):
    """Calculate the number of destination plates"""
    list_destination_plate = []
    for pair in list_part_count:
        part_name = pair[0]
        times_needed = pair[1]
        primer_f, primer_r, template = get_primers_template(part_name, list_source_wells)

        count = 0
        for sample in primer_r:
            if int(sample[8]) <= int(sample[7]):
                for i in range(0, int(sample[8]-count)):
                    count+=1
                    list_destination_plate.append(sample)
            else:
                for j in range(0, int(sample[7]-count)):
                    list_destination_plate.append(sample)

    return list_destination_plate


def get_part_info(found_list, name):
    for part in found_list:
        part_name, part_type, part_length, part_conc, part_vol, source_plate, source_well, num_well = part
        if part_name == name:
            part_conc = float(part_conc)
            return part_type, part_length, part_conc
    return None


def calc_wells_available_volume(list_wells, times_needed, conc_primer, total_vol, res_vol, min_vol, robot):
    total_vol_primers = []
    for well_part in list_wells:
        part_name, sample_name, sample_direction, sample_type, sample_wellconcentration, sample_wellvolume, sample_platename, sample_wellname, sample_num_well = well_part

        '''Volume needed of the primer '''
        primer_f_vol_needed = (float(conc_primer) * float(total_vol))/float(well_part[4])

        '''Rounding the part volume according to machine resolution'''
        vol_primer_add = calc.round_at(primer_f_vol_needed, res_vol)

        '''Minimal dispense volume'''
        vol_part_add = max(vol_primer_add, min_vol)

        '''Calculate how many 'vol_part_add' have in the total volume in one well'''
        available_vol = max(float(sample_wellvolume) - robot.dead_vol, 0)

        '''total times per well'''
        times_available = int(available_vol / vol_part_add)
        total_vol_primers.append([part_name, sample_name, sample_direction, sample_type, sample_wellconcentration, sample_wellvolume, times_needed, times_available, vol_part_add, sample_platename, sample_wellname, sample_num_well])

    return total_vol_primers


def calc_volume_primers_template(primer_f, primer_r, template, count, mix_parameters, dispenser_parameters, robot):
    total_vol_primers = []
    template_conc, conc_primer_f, conc_primer_r, per_buffer, per_phusion, per_dntps, total_vol, add_water = mix_parameters
    machine, min_vol, res_vol, dead_vol = dispenser_parameters

    total_vol_primers.extend(calc_wells_available_volume(primer_f, count, conc_primer_f, total_vol, res_vol, min_vol, robot))
    total_vol_primers.extend(calc_wells_available_volume(primer_r, count, conc_primer_r, total_vol, res_vol, min_vol, robot))
    total_vol_primers.extend(calc_wells_available_volume(template, count, template_conc, total_vol, res_vol, min_vol, robot))

    return total_vol_primers


def get_primers_template(part_name, found_list):
    primer_f = []
    primer_r = []
    template = []
    for list in found_list:
        if list[0] == part_name:
            if list[3] == 'Primer':
                if list[2] == 'FWD':
                    primer_f.append(list)
                else:
                    primer_r.append(list)
            else:
                template.append(list)
    return primer_f, primer_r, template


def calc_part_volumes_in_plate(count_unique_list, found_list, mix_parameters, dispenser_parameters, robot):
    total_vol_parts = []

    for pair in count_unique_list:
        part_name = pair[0]
        times_needed = pair[1]  # Number of times to replicate the sample
        primer_f, primer_r, template = get_primers_template(part_name, found_list)
        total_vol_parts.extend(calc_volume_primers_template(primer_f, primer_r, template, times_needed, mix_parameters, dispenser_parameters, robot))
        print(total_vol_parts)

    return total_vol_parts


def calc_mixer_volumes(mix_parameters):
    template_conc, primer_f, primer_r, per_buffer, per_phusion, per_dntps, total_vol, add_water = mix_parameters

    '''Calculate buffer and enzimes'''
    phusion_vol = (per_phusion * total_vol) / 100
    buffer_vol = (per_buffer * total_vol) / 100
    dNTPS_vol = (per_dntps * total_vol) / 100
    total_vol_buffer = phusion_vol + buffer_vol + dNTPS_vol
    vol_for_mixer = [phusion_vol, buffer_vol, dNTPS_vol, total_vol_buffer]
    return vol_for_mixer


def get_min_water_vol(out_water):
    min_water_vol = MAX_VALUE
    for item in out_water:
        name, vol, well = item
        if min_water_vol > vol:
            min_water_vol = vol
    return min_water_vol


def reajust_mixer_water_volumes(out_master_mix, out_water, min_water_vol):
    reaj_out_master_mix = []
    reaj_out_water = []

    for item in out_water:
        name, vol, well = item
        new_vol = vol - min_water_vol
        reaj_out_water.append([name,new_vol,well])

    for item in out_master_mix:
        name, vol, well = item
        new_name = 'Mastermix_PCR'
        new_vol = vol + min_water_vol
        reaj_out_master_mix.append([new_name,new_vol,well])
    return reaj_out_master_mix, reaj_out_water


def add_on_list(lista, item):
    for i in range(0, len(lista)):
        if lista[i] == item:
            return False
    return True


def verify_wells_available_volume(list_wells, part_name, robot):
    alert = []
    list_source_wells = []
    list_source_wells_joint = []
    tot_times = 0
    total_available_vol = 0
    for well in list_wells:
        part_name, sample_name, sample_direction, sample_type, sample_wellconcentration, available_vol, times_needed, times_available, vol_part_add, sample_platename, sample_wellname, sample_num_well = well
        tot_times += times_available
        if int(times_needed) <= times_available:
            list_source_wells.append(well)
            return list_source_wells, alert
        else:
            total_available_vol += available_vol
            list_source_wells_joint.append(well)
            if tot_times >= int(times_needed):
                return list_source_wells_joint, alert

    vol_need = float(list_wells[0][8])*int(list_wells[0][6])
    alert = 'Not enough volume of: ' + str(list_wells[0][1]) + ' to synthesize: '+ str(part_name) +'. Available volume after remove dead volume: ' + str(total_available_vol-robot.dead_vol*len(list_wells)) + ' needed: ' + str(vol_need)

    return None, alert


def verify_samples_volume(vol_for_part, count_unique_list, robot):
    '''Volume needed of parts for the experiment'''
    alert = []
    list_source_wells = []
    list_part_low_vol = []
    for pair in count_unique_list:
        part_name = pair[0]
        times_needed = pair[1]  # Number of times it appears in experiment
        print(part_name)

        '''Get list of wells'''
        primer_f, primer_r, template = get_primers_template(part_name, vol_for_part)
        print(primer_f, primer_r, template)
        list_source_wells_primerF, alertF = verify_wells_available_volume(primer_f, part_name, robot)
        list_source_wells_primerR, alertR = verify_wells_available_volume(primer_r, part_name, robot)
        list_source_wells_template, alertT = verify_wells_available_volume(template, part_name, robot)

        if len(alertF) > 0 or len(alertR) > 0 or len(alertT) > 0:
            if len(alertF) > 0: alert.append(alertF)
            if len(alertR) > 0: alert.append(alertR)
            if len(alertT) > 0: alert.append(alertT)
            return None, None, alert
        else:
            list_source_wells.extend(list_source_wells_primerF)
            list_source_wells.extend(list_source_wells_primerR)
            list_source_wells.extend(list_source_wells_template)

    return list_source_wells, list_part_low_vol, alert


def create_and_populate_sources_plate(found_list):
    plates_in = parser.create_source_plates_from_foundlist(found_list)
    plates_in = parser.list_to_source_plates(found_list, plates_in)
    return plates_in


def find_templates_database(unique_list):
    ''' Verify parts in database '''
    found_list = []
    missing_list = []
    for part in unique_list:
        #Need to search for sub_samples in wells
        wells = Well.objects.filter(samples__sub_sample_id__name__exact=str(part[0]))

        if len(wells) > 0:
            for well in wells:
                #To be sure it is not a mix of samples and has only one sample on well
                if well.samples.count() == 1:
                    for subsample in well.samples.all():
                        if well.volume > 0:
                            lista = [part[0], subsample.name, 0, subsample.sample_type, float(well.concentration), float(well.volume), well.plate.name, well.name, int(well.plate.num_well)]
                            found_list.append(lista)
                        else:
                            missing_list.append(part[0])
        else:
            missing_list.append(part[0])

    return found_list, missing_list


def find_primers_database(unique_list, found_parts):
    ''' Verify parts in database '''
    found_list = found_parts
    missing_list = []
    for part in unique_list:
        primer_fwd = []
        primer_rev = []
        samples = Sample.objects.filter(name__exact=str(part[0]))
        for sample in samples:
            if sample.primer_id is not None:
                for primer in sample.primer_id.all():
                    if primer.direction == 'FWD':
                        primer_fwd.append(primer)
                    elif primer.direction == 'REV':
                        primer_rev.append(primer)

                # sample has two or more fwd and rev primers
                if len(primer_fwd) > 0 and len(primer_rev) > 0:
                    wells_fwd = []
                    wells_rev = []
                    for primer in primer_fwd:
                        wells_fwd = Well.objects.filter(samples__name__exact=str(primer))
                        if len(wells_fwd) > 0:
                            for well in wells_fwd:
                                lista = [part[0], primer.name, str(primer.direction), primer.sample_type, float(well.concentration), float(well.volume), well.plate.name, well.name, int(well.plate.num_well)]
                                found_list.append(lista)
                        else:
                            missing_list.append(str(part[0])+' ('+str(primer)+')')

                    for primer in primer_rev:
                        wells_rev = Well.objects.filter(samples__name__exact=str(primer))
                        if len(wells_rev) > 0:
                            for well in wells_rev:
                                lista = [part[0], primer.name, str(primer.direction), primer.sample_type, float(well.concentration), float(well.volume), well.plate.name, well.name, int(well.plate.num_well)]
                                found_list.append(lista)
                        else:
                            missing_list.append(str(part[0])+' ('+str(primer)+')')
                else:
                    missing_list.append(part[0])
            else:
                missing_list.append(part[0])

    return found_list, missing_list


def get_part_count(reader):
    list_part_count = []
    for line in reader:
        line = line.rstrip()
        if line:
            set = line.split(',')
            list_part_count.append(list(set))
    return list_part_count


def run_pcr_db(path, filename, dispenser_parameters, mix_parameters, out_num_well, pattern, use_high_low_chip_mantis, user):
    total_alert = []
    name_machine, min_vol, res_vol, dead_vol = dispenser_parameters
    robot = machine.Machine(name_machine, min_vol, res_vol, dead_vol)
    template_conc, primer_f, primer_r, per_buffer, per_phusion, per_dntps, total_vol, add_water = mix_parameters

    ''' Create read files'''
    filein = file.verify(path + "/" + filename)

    ''' Create write files'''
    db_mantis_name = 'mantis_' + str(os.path.splitext(filename)[0]) + '.csv'
    db_robot_name = str(robot.name) + "_" + str(os.path.splitext(filename)[0]) + '.csv'
    file_mantis = file.create(path + "/docs/" + db_mantis_name, 'w')
    file_robot = file.create(path + "/docs/" + db_robot_name, 'w')
    mantis_csv = file.create_writer_csv(file_mantis)
    robot_csv = file.create_writer_csv(file_robot)

    ''' Get parts and number of repetitions desirable'''
    list_part_count = get_part_count(filein)

    """Verify the parts on database"""
    found_parts, missing_parts = find_templates_database(list_part_count)

    if len(missing_parts) > 0:
        for item in missing_parts:
            total_alert.append('Parts not found in database or not enough volume: ' + str(item))
        return total_alert, None, None, None, None

    else:
        '''Verify the primers for the parts'''
        found_list, missing_primers = find_primers_database(list_part_count, found_parts)

        if len(missing_primers) > 0:
            for item in missing_primers:
                total_alert.append('Primers not found in database for ' + str(item))
            return total_alert, None, None, None, None

        else:
            # """Create and Populate Source Plates"""
            # plates_in = create_and_populate_sources_plate(found_list)

            """Calculate the part volumes"""
            vol_for_part = calc_part_volumes_in_plate(list_part_count, found_list, mix_parameters, dispenser_parameters, robot)

            """Verify parts volume in source plate"""
            list_source_wells, list_part_low_vol, alert = verify_samples_volume(vol_for_part, list_part_count, robot)
            if len(alert) > 0:
                return alert, None, None, None, None

            else:
                """Create a destination plates"""
                plates_out = create_destination_plates(list_part_count, list_source_wells, out_num_well)

                """Populate plate"""
                plates_out, out_dispenser, out_master_mix, out_water, alert = populate_destination_plates(plates_out, list_part_count, list_source_wells, mix_parameters, pattern)

                """Mantis output file"""
                file.set_mantis_import_header(mantis_csv)
                min_water_vol = get_min_water_vol(out_water)

                """Mixer Recipe"""
                mixer_recipe = calc_mixer_volumes(mix_parameters)
                phusion_vol, buffer_vol, dNTPS_vol, total_vol_buffer = mixer_recipe

                chip_mantis = []

                if add_water is True:
                    '''Add water in Master Mix and Remove from Water list'''
                    out_master_mix, out_water = reajust_mixer_water_volumes(out_master_mix, out_water, min_water_vol)

                    '''Master Mix recipe output'''
                    mixer_recipe_title = ["Phusion", "Buffer", "dNTPs", "Water", "Master Mix"]
                    min_water_vol = round(min_water_vol, 2)
                    total_vol_buffer += min_water_vol
                    mixer_recipe = [round(phusion_vol, 2), round(buffer_vol, 2), round(dNTPS_vol, 2),
                                    round(min_water_vol, 2), round(total_vol_buffer, 2)]
                    mixer_recipe_zip = zip(mixer_recipe, mixer_recipe_title)

                else:
                    mixer_recipe_title = ["Phusion", "Buffer", "dNTPs", "Water", "Master Mix"]
                    mixer_recipe_zip = zip(mixer_recipe, mixer_recipe_title)

                if use_high_low_chip_mantis is True:
                    master_high, master_low = file.write_dispenser_mantis_in_low_high_chip(mantis_csv, out_master_mix)
                    water_high, water_low = file.write_dispenser_mantis_in_low_high_chip(mantis_csv, out_water)

                    chip_matis_title = ["Master mix in high chip", "Master mix in low chip", "Water in high chip",
                                        "Water in low chip"]
                    chip_matis_vol = [round(master_high, 2), round(master_low, 2), round(water_high, 2),
                                      round(water_low, 2)]
                    chip_mantis_zip = zip(chip_matis_title, chip_matis_vol)

                else:
                    master_total = file.write_dispenser_mantis(mantis_csv, out_master_mix)
                    water_total = file.write_dispenser_mantis(mantis_csv, out_water)

                    chip_matis_title = ["Master mix total volume", "Water total volume"]
                    chip_matis_vol = [round(master_total, 2), round(water_total, 2)]
                    chip_mantis_zip = zip(chip_matis_title, chip_matis_vol)

                ''' Robot Dispenser parts '''
                file.set_echo_header(robot_csv)
                file.write_dispenser_echo(out_dispenser, robot_csv)

    db_mantis = db.save_file(db_mantis_name, 'PCR_DB', user)
    db_robot = db.save_file(db_robot_name, 'PCR_DB', user)
    return total_alert, db_mantis, db_robot, mixer_recipe_zip, chip_mantis_zip

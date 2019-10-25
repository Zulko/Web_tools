from ..biofoundry import db
from ..misc import calc, file, parser
from ..container import plate, machine
import sys, os
from db.models import Plate, Well, Sample


# Dispense modo in plate
BY_ROW = 0
BY_COL = 1
MAX_VALUE = 999999


def get_localization_vol(part_name, list_source_wells):
    for i, item in enumerate(list_source_wells):
        sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, times_available, vol_part_add, plate_in_name, wellD_name = list_source_wells[i]
        if part_name == sample_name and times_available > 0:
            new_times_available = times_available - 1
            list_source_wells[i] = [sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, new_times_available, vol_part_add, plate_in_name, wellD_name]
            # print(part_name, times_available, wellD_name)
            return list_source_wells, list_source_wells[i]
        # elif part_name == sample_name and times_available == 0:
        #     print(part_name, times_available, wellD_name)


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


def populate_destination_plates(plates_out, list_destination_plate, list_source_wells, mix_parameters, pattern):
    alert = []
    part_fmol, bb_fmol, total_vol, per_buffer, per_rest_enz, per_lig_enz, add_water = mix_parameters
    out_dispenser = []
    out_master_mix = []
    out_water = []
    for set in list_destination_plate:
        p, i, j = get_plate_with_empty_well(plates_out, pattern)
        total_parts_vol = 0
        for part in set:
            list_source_wells, part = get_localization_vol(part, list_source_wells)
            sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, new_times_available, vol_part_add, source_plate, source_well = part
            final_conc = calc.fmol_by_parttype(sample_type, bb_fmol, part_fmol)

            """ Adding parts in destination plate """
            plates_out[p].wells[i][j].samples.append(plate.Sample(sample_name, sample_type, sample_length, final_conc, vol_part_add))
            out_dispenser.append([sample_name, sample_type, source_plate, source_well, vol_part_add, plates_out[p].name, plates_out[p].wells[i][j].name, plates_out[p].id])

            """ Sum of total volume of parts """
            total_parts_vol += vol_part_add

        '''Calculate buffer and enzimes'''
        vol_for_mixer = calc_mixer_volumes(mix_parameters)
        buffer_vol, rest_enz_vol, lig_enz_vol, total_vol_buffer = vol_for_mixer

        '''Total water volume in well'''
        vol_water = total_vol - (total_vol_buffer + total_parts_vol)

        if vol_water >= 0:
            ''' Add receipts in list destination'''
            out_master_mix.append(['buffer', total_vol_buffer, plates_out[p].wells[i][j].name])
            out_water.append(['water', vol_water, plates_out[p].wells[i][j].name])

            ''' Add receipts in destination plate '''
            plates_out[p].wells[i][j].samples.append(plate.Sample('Mastermix_Moclo', None, None, None, total_vol_buffer))
            plates_out[p].wells[i][j].samples.append(plate.Sample('Water', None, None, None, vol_water))
        else:
            alert.append('In constructor: ' + str(set) + '. The water volume is negative.')

    return plates_out, out_dispenser, out_master_mix, out_water, alert


def create_plate(num_wells, name):
    rows, cols = calc.rows_columns(int(num_wells))
    new_plate = plate.Plate(rows, cols, name)
    return new_plate


def create_destination_plates(list_destination_plate, out_num_well):
    plates_out = []
    num_receipts = len(list_destination_plate)
    num_plates = calc.num_destination_plates(num_receipts, out_num_well)

    for i in range(0, num_plates):
        plates_out.append(create_plate(out_num_well, 'Destination_' + str(i+1)))
    return plates_out


def create_entry_list_for_destination_plate(lists_parts, list_part_low_vol):
    """Calculate the number of destination plates"""
    list_destination_plate = []
    for set in lists_parts:
        low_vol = False
        for part in set:
            for low_vol_part in list_part_low_vol:
                name_lvp = low_vol_part[0]
                vol_lvp = low_vol_part[1]
                vol_lvp = round(vol_lvp, 2)
                if part == name_lvp:
                    # print('For Contructor: ' + str(set) + ' There is not enough volume for sample: ' + str(
                    #     part) + '. Required : ' + str(vol_lvp))
                    low_vol = True

        if low_vol is False:
            '''Add constructor to list for destination plate'''
            list_destination_plate.append(set)
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
    for well_pf in list_wells:
        part_name, sample_name, sample_direction, sample_type, sample_wellconcentration, sample_wellvolume, sample_platename, sample_wellname, sample_num_well = well_pf

        '''Volume needed of the primer '''
        primer_f_vol_needed = (float(conc_primer) * float(total_vol))/float(well_pf[4])

        '''Rounding the part volume according to machine resolution'''
        vol_primer_add = calc.round_at(primer_f_vol_needed, res_vol)

        '''Minimal dispense volume'''
        vol_part_add = max(vol_primer_add, min_vol)

        '''Calculate how many 'vol_part_add' have in the total volume in one well'''
        available_vol = max(float(sample_wellvolume) - robot.dead_vol, 0)

        '''total times per well'''
        times_available = int(available_vol / vol_part_add)
        print(available_vol, vol_part_add)

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
    # print(found_list)
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


def calc_part_volumes_in_plate(count_unique_list, found_list, plates_in, mix_parameters, dispenser_parameters, robot):
    # part_fmol, bb_fmol, total_vol, buffer, rest_enz, lig_enz, add_water = mix_parameters
    template_conc, vol_primer_f, vol_primer_r, per_buffer, per_phusion, per_dntps, total_vol, add_water = mix_parameters
    machine, min_vol, res_vol, dead_vol = dispenser_parameters
    total_vol_parts = []

    for pair in count_unique_list:
        part_name = pair[0]
        times_needed = pair[1]  # Number of times to replicate the sample
        primer_f, primer_r, template = get_primers_template(part_name, found_list)
        total_vol_parts.extend(calc_volume_primers_template(primer_f, primer_r, template, times_needed, mix_parameters, dispenser_parameters, robot))

    return total_vol_parts


def calc_mixer_volumes(mix_parameters):
    part_fmol, bb_fmol, total_vol, per_buffer, per_rest_enz, per_lig_enz, add_water = mix_parameters

    '''Calculate buffer and enzimes'''
    buffer_vol = (per_buffer * total_vol) / 100
    rest_enz_vol = (per_rest_enz * total_vol) / 100
    lig_enz_vol = (per_lig_enz * total_vol) / 100
    total_vol_buffer = buffer_vol + rest_enz_vol + lig_enz_vol
    vol_for_mixer = [buffer_vol, rest_enz_vol, lig_enz_vol, total_vol_buffer]
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
        # new_name = name+'+water'
        new_name = 'Mastermix_Moclo'
        new_vol = vol + min_water_vol
        reaj_out_master_mix.append([new_name,new_vol,well])
    return reaj_out_master_mix, reaj_out_water


def add_on_list(lista, item):
    for i in range(0, len(lista)):
        if lista[i] == item:
            return False
    return True


def verify_wells_available_volume(list_wells, part_name):
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
    print(list_wells[0][6], list_wells[0][7], list_wells[0][5])
    vol_need = float(list_wells[0][8])*int(list_wells[0][6])
    alert = 'Not enough volume of: ' + str(list_wells[0][1]) + ' to build: '+ str(part_name) +'. Available volume: ' + str(total_available_vol) + ' needed: ' + str(vol_need)
    print(alert)
    return None, alert


def verify_samples_volume(vol_for_part, count_unique_list, robot):
    '''Volume needed of parts for the experiment'''
    list_source_wells = []
    list_part_low_vol = []
    for pair in count_unique_list:
        found = False
        tot_times = 0
        part_info = []
        part_name = pair[0]
        times_needed = pair[1]  # Number of times it appears in experiment

        '''Get list of wells'''
        primer_f, primer_r, template = get_primers_template(part_name, vol_for_part)
        list_source_wells_primerF, alertF = verify_wells_available_volume(primer_f, part_name)
        list_source_wells_primerR, alertR = verify_wells_available_volume(primer_r, part_name)
        list_source_wells_template, alertT = verify_wells_available_volume(template, part_name)

        print(list_source_wells_primerF)
        print(list_source_wells_primerR)
        print(list_source_wells_template)

        # for part in vol_for_part:
        #     sample_name, sample_type, sample_length, sample_concentration, sample_volume, sample_times_needed, vol_part_add, plate_in_name, wellD_name = part
        #     if part_name == sample_name:
        #         '''Calculate how many 'vol_part_add' have in the total volume in one well'''
        #         available_vol = float(sample_volume) - robot.dead_vol
        #         '''total times per well'''
        #         times_available = int(available_vol/vol_part_add)
        #         '''total times in all database'''
        #         tot_times += times_available
        #         part_info.append(part)
        #
        #         if int(sample_times_needed) <= times_available:
        #             list_source_wells.append([sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, times_available, vol_part_add, plate_in_name, wellD_name])
        #             break
        # if int(tot_times) >= int(times_needed):
        #     for part in part_info:
        #         sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, vol_part_add, plate_in_name, wellD_name = part
        #         # Calculate how many 'vol_part_add' have in the total volume in one well
        #         available_vol = float(sample_volume) - robot.dead_vol
        #         # total times per well
        #         times_available = int(available_vol / vol_part_add)
        #         list_source_wells.append([sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, times_available, vol_part_add, plate_in_name, wellD_name])
        # else:
        #     for part in part_info:
        #         sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, vol_part_add, plate_in_name, wellD_name = part
        #         total_vol_part = times_needed*vol_part_add
        #         print('Not enough volume for sample: ' + str(part_name) + ' available: ' + str(sample_volume) + " need: " + str(round(total_vol_part+robot.dead_vol,2)))
        #         alert.append(['Not enough volume for sample: ' + str(part_name) + ' available: ' + str(sample_volume) + " need: " + str(round(total_vol_part+robot.dead_vol,2))])
        #         list_part_low_vol.append([sample_name, total_vol_part])

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
        set = line.strip("\n").split(',')
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
            """Create and Populate Source Plates"""
            plates_in = create_and_populate_sources_plate(found_list)

            """Calculate the part volumes"""
            vol_for_part = calc_part_volumes_in_plate(list_part_count, found_list, plates_in, mix_parameters, dispenser_parameters, robot)
            # print(vol_for_part)

            """Verify parts volume in source plate"""
            list_source_wells, list_part_low_vol, alert = verify_samples_volume(vol_for_part, list_part_count, robot)
            if len(alert) > 0:
                for item in alert:
                    total_alert.append(item)

        #     """Create entry list for destination plates"""
        #     list_destination_plate = create_entry_list_for_destination_plate(lists_parts, list_part_low_vol)
        #
        #     if len(list_destination_plate) > 0:
        #         """Create a destination plates"""
        #         plates_out = create_destination_plates(list_destination_plate, out_num_well)
        #
        #         """Populate plate"""
        #         plates_out, out_dispenser, out_master_mix, out_water, alert = populate_destination_plates(plates_out, list_destination_plate, list_source_wells, mix_parameters, pattern)
        #         # file.write_plate_by_col(plates_out)
        #
        #         """Mantis output file"""
        #         file.set_mantis_import_header(mantis_csv)
        #         min_water_vol = get_min_water_vol(out_water)
        #
        #         # water to add in master mix, enzime
        #         mixer_recipe = calc_mixer_volumes(mix_parameters)
        #         buffer_vol, rest_enz_vol, lig_enz_vol, total_vol_buffer = mixer_recipe
        #
        #         chip_mantis = []
        #
        #         if add_water is True:
        #             ''' Add water in Master Mix and Remove from Water list'''
        #             out_master_mix, out_water = reajust_mixer_water_volumes(out_master_mix, out_water, min_water_vol)
        #
        #             '''Master Mix recipe output'''
        #             mixer_recipe_title = ["Buffer", "Restriction Enzyme", "Ligase Enzyme", "Water", "Master Mix"]
        #             min_water_vol = round(min_water_vol, 2)
        #             total_vol_buffer += min_water_vol
        #             mixer_recipe = [round(buffer_vol, 2), round(rest_enz_vol, 2), round(lig_enz_vol, 2),
        #                             round(min_water_vol, 2), round(total_vol_buffer, 2)]
        #             mixer_recipe_zip = zip(mixer_recipe, mixer_recipe_title)
        #
        #         else:
        #             mixer_recipe_title = ["Buffer", "Restriction Enzime", "Ligase Enzime", "Total Buffer"]
        #             mixer_recipe_zip = zip(mixer_recipe, mixer_recipe_title)
        #
        #         if use_high_low_chip_mantis is True:
        #             master_high, master_low = file.write_dispenser_mantis_in_low_high_chip(mantis_csv, out_master_mix)
        #             water_high, water_low = file.write_dispenser_mantis_in_low_high_chip(mantis_csv, out_water)
        #
        #             chip_matis_title = ["Master mix in high chip", "Master mix in low chip", "Water in high chip",
        #                                 "Water in low chip"]
        #             chip_matis_vol = [round(master_high, 2), round(master_low, 2), round(water_high, 2),
        #                               round(water_low, 2)]
        #             chip_mantis_zip = zip(chip_matis_title, chip_matis_vol)
        #
        #         else:
        #             master_total = file.write_dispenser_mantis(mantis_csv, out_master_mix)
        #             water_total = file.write_dispenser_mantis(mantis_csv, out_water)
        #
        #             chip_matis_title = ["Master mix total volume", "Water total volume"]
        #             chip_matis_vol = [round(master_total, 2), round(water_total, 2)]
        #             chip_mantis_zip = zip(chip_matis_title, chip_matis_vol)
        #
        #         ''' Robot Dispenser parts '''
        #         file.set_echo_header(robot_csv)
        #         file.write_dispenser_echo(out_dispenser, robot_csv)
        #
        #     else:
        #         return total_alert, None, None, None, None
        #         # sys.exit()
    # db_mantis = db.save_file(db_mantis_name, 'Moclo_DB', user)
    # db_robot = db.save_file(db_robot_name, 'Moclo_DB', user)
    # return total_alert, file_mantis, file_robot, mixer_recipe_zip, chip_mantis_zip

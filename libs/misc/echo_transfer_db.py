import sys, os, itertools

from django.core.exceptions import ObjectDoesNotExist

from ..biofoundry import db
from libs.misc import file, calc, parser
from libs.container import plate, machine
from db.models import Plate, Well, Sample


# Dispense modo in plate
BY_ROW = 0
BY_COL = 1
MAX_VALUE = 999999


def get_name_from_alias(part, found_list):
    for line in found_list:
        if part == line[1]:
            return line[0]


def get_localization_vol(part, list_source_wells, found_list):
    for i, item in enumerate(list_source_wells):
        # print(list_source_wells[i])
        sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, times_available, vol_part_add, plate_in_name, plate_barcode, wellD_name = list_source_wells[i]
        part_sample = get_name_from_alias(part, found_list)
        if part_sample == sample_name and times_needed > 0:
            new_times_needed = times_needed - 1
            list_source_wells[i] = [sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, new_times_needed, vol_part_add, plate_in_name, plate_barcode, wellD_name]
            return list_source_wells, list_source_wells[i]


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


def populate_destination_plates(plates_out, list_source_wells, lists_parts, lists_volume, found_list, pattern):
    alert = []
    out_dispenser = []
    out_master_mix = []
    out_water = []
    for set_p, set_v in zip(lists_parts, lists_volume):
        p, i, j = get_plate_with_empty_well(plates_out, pattern)
        total_parts_vol = 0
        for partalias, vol in zip(set_p, set_v):
            list_source_wells, part = get_localization_vol(partalias, list_source_wells, found_list)
            list_source_wells, part = get_localization_vol(partalias, list_source_wells, found_list)
            name, sample_direction, sample_type, sample_wellconcentration, available_vol, times_needed, \
            times_available, vol_part_add, sample_platename, sample_plate_barcode, sample_wellname = part

            """Adding parts in destination plate """
            plates_out[p].wells[i][j].samples.append(
                plate.Sample(partalias, sample_direction, sample_type, sample_wellconcentration, vol)
            )
            out_dispenser.append(
                [name, partalias, sample_type, sample_plate_barcode, sample_platename, sample_wellname, vol,
                 plates_out[p].name, plates_out[p].name, plates_out[p].wells[i][j].name, plates_out[p].id]
            )

    return plates_out, out_dispenser, out_master_mix, out_water, alert


def create_plate(num_wells, name):
    rows, cols = calc.rows_columns(int(num_wells))
    new_plate = plate.Plate(rows, cols, name)
    return new_plate


def create_destination_plates(lists_parts, out_num_well):
    num = Plate.objects.latest('id').id
    plates_out = []
    num_receipts = 0
    for set in lists_parts:
        num_receipts += 1

    num_plates = calc.num_destination_plates(num_receipts, out_num_well)
    for i in range(0, num_plates):
        num = num+1
        plates_out.append(create_plate(out_num_well, 'GF' + '{0:05}'.format(num)))
    return plates_out


# def create_entry_list_for_destination_plate(list_source_wells, list_part_count):
#     print('create_entry_list_for_destination_plate')
#     """Calculate the number of destination plates"""
#     list_destination_plate = []
#     for pair in list_part_count:
#         part_name = pair[0]
#         times_needed = pair[1]
#         primer_f, primer_r, template = get_primers_template(part_name, list_source_wells)
#
#         count = 0
#         for sample in primer_r:
#             if int(sample[8]) <= int(sample[7]):
#                 for i in range(0, int(sample[8]-count)):
#                     count+=1
#                     list_destination_plate.append(sample)
#             else:
#                 for j in range(0, int(sample[7]-count)):
#                     list_destination_plate.append(sample)
#
#     return list_destination_plate


# def get_part_info(found_list, name):
#     print('get_part_info')
#     for part in found_list:
#         part_name, part_type, part_length, part_conc, part_vol, source_plate, source_well, num_well = part
#         if part_name == name:
#             part_conc = float(part_conc)
#             return part_type, part_length, part_conc
#     return None


# def calc_wells_available_volume(list_wells, times_needed, conc_primer, total_vol, res_vol, min_vol, robot):
#     print('calc_wells_available_volume')
#     total_vol_primers = []
#     for well_part in list_wells:
#         part_name, sample_name, sample_direction, sample_type, sample_wellconcentration, sample_wellvolume, sample_platename, sample_wellname, sample_num_well = well_part
#
#         '''Volume needed of the primer '''
#         primer_f_vol_needed = (float(conc_primer) * float(total_vol))/float(well_part[4])
#
#         '''Rounding the part volume according to machine resolution'''
#         vol_primer_add = calc.round_at(primer_f_vol_needed, res_vol)
#
#         '''Minimal dispense volume'''
#         vol_part_add = max(vol_primer_add, min_vol)
#
#         '''Calculate how many 'vol_part_add' have in the total volume in one well'''
#         available_vol = max(float(sample_wellvolume) - robot.dead_vol, 0)
#
#         '''total times per well'''
#         times_available = int(available_vol / vol_part_add)
#         total_vol_primers.append([part_name, sample_name, sample_direction, sample_type, sample_wellconcentration, sample_wellvolume, times_needed, times_available, vol_part_add, sample_platename, sample_wellname, sample_num_well])
#
#     return total_vol_primers


# def calc_volume_primers_template(primer_f, primer_r, template, count, mix_parameters, dispenser_parameters, robot):
#     print('calc_volume_primers_template')
#     total_vol_primers = []
#     template_conc, conc_primer_f, conc_primer_r, per_buffer, per_phusion, per_dntps, total_vol, add_water = mix_parameters
#     machine, min_vol, res_vol, dead_vol = dispenser_parameters
#
#     total_vol_primers.extend(calc_wells_available_volume(primer_f, count, conc_primer_f, total_vol, res_vol, min_vol, robot))
#     total_vol_primers.extend(calc_wells_available_volume(primer_r, count, conc_primer_r, total_vol, res_vol, min_vol, robot))
#     total_vol_primers.extend(calc_wells_available_volume(template, count, template_conc, total_vol, res_vol, min_vol, robot))
#
#     return total_vol_primers


# def get_primers_template(part_name, found_list):
#     print('get_primers_template')
#     primer_f = []
#     primer_r = []
#     template = []
#     for list in found_list:
#         if list[0] == part_name:
#             if list[3] == 'Primer':
#                 if list[2] == 'FWD':
#                     primer_f.append(list)
#                 else:
#                     primer_r.append(list)
#             else:
#                 template.append(list)
#     return primer_f, primer_r, template


def check_sample_volume_plate(count_unique_vol_list, dispenser_parameters):
    total_vol_parts = []
    for pair in count_unique_vol_list:
        vector, alert = calc_part_volumes_in_plate(pair, dispenser_parameters)
        if vector is not None:
            total_vol_parts.extend(vector)
        else:
            return None, alert
    return total_vol_parts, None


def calc_part_volumes_in_plate(pair, dispenser_parameters):
    machine, min_vol, res_vol, dead_vol = dispenser_parameters
    total_vol_parts = []
    part_name, total_vol, times_needed = pair
    wells = Well.objects.filter(samples__alias__exact=str(part_name))
    available_vol = 0
    for well in wells:
        if well.samples.count() == 1 and well.active is True:
            for sample in well.samples.all():
                volume = 0
                times_available = 0
                vol_part_add = 0
                total_vol_needed = total_vol
                available_vol += max(float(well.volume) - dead_vol, 0)
                total_vol_parts.append([sample.name, sample.direction, sample.sample_type, well.concentration,
                                        well.volume, times_needed, times_available, vol_part_add,
                                        well.plate.name, well.plate.barcode, well.name])
                if available_vol >= total_vol_needed:
                    return total_vol_parts, None
    alert = 'Not enough volume for %s. Volume needed: %d, available: %d', part_name, total_vol, available_vol
    return None, alert


# def calc_mixer_volumes(mix_parameters):
#     print('calc_mixer_volumes')
#     template_conc, primer_f, primer_r, per_buffer, per_phusion, per_dntps, total_vol, add_water = mix_parameters
#
#     '''Calculate buffer and enzimes'''
#     phusion_vol = (per_phusion * total_vol) / 100
#     buffer_vol = (per_buffer * total_vol) / 100
#     dNTPS_vol = (per_dntps * total_vol) / 100
#     total_vol_buffer = phusion_vol + buffer_vol + dNTPS_vol
#     vol_for_mixer = [phusion_vol, buffer_vol, dNTPS_vol, total_vol_buffer]
#     return vol_for_mixer


# def get_min_water_vol(out_water):
#     print('get_min_water_vol')
#     min_water_vol = MAX_VALUE
#     for item in out_water:
#         name, vol, well = item
#         if min_water_vol > vol:
#             min_water_vol = vol
#     return min_water_vol


# def reajust_mixer_water_volumes(out_master_mix, out_water, min_water_vol):
#     print('reajust_mixer_water_volumes')
#     reaj_out_master_mix = []
#     reaj_out_water = []
#
#     for item in out_water:
#         name, vol, well = item
#         new_vol = vol - min_water_vol
#         reaj_out_water.append([name,new_vol,well])
#
#     for item in out_master_mix:
#         name, vol, well = item
#         new_name = 'Mastermix_PCR'
#         new_vol = vol + min_water_vol
#         reaj_out_master_mix.append([new_name,new_vol,well])
#     return reaj_out_master_mix, reaj_out_water


def add_on_list(lista, item):
    for i in range(0, len(lista)):
        if lista[i] == item:
            return False
    return True


# def verify_wells_available_volume(list_wells, partname, robot):
#     print('verify_wells_available_volume')
#     alert = []
#     list_source_wells = []
#     list_source_wells_joint = []
#     tot_times = 0
#     total_available_vol = 0
#     for well in list_wells:
#         part_name, sample_direction, sample_type, sample_wellconcentration, available_vol, times_needed, times_available, vol_part_add, sample_platename, sample_wellname = well
#         tot_times += times_available
#         if int(times_needed) <= times_available:
#             list_source_wells.append(well)
#             return list_source_wells, alert
#         else:
#             total_available_vol += available_vol
#             list_source_wells_joint.append(well)
#             if tot_times >= int(times_needed):
#                 return list_source_wells_joint, alert
#
#     vol_need = float(list_wells[0][8])*int(list_wells[0][6])
#     alert = 'Not enough volume of: ' + str(list_wells[0][1]) + ' to synthesize: '+ str(partname.name) +'. Available volume after remove dead volume: ' + str(total_available_vol-robot.dead_vol*len(list_wells)) + ' needed: ' + str(vol_need)
#     print(alert)
#     return None, alert


# def verify_samples_volume(vol_for_part, count_unique_list, robot):
#     print('verify_samples_volume')
#     alert = []
#     '''Volume needed of parts for the experiment'''
#     list_source_wells = []
#     for pair in count_unique_list:
#         part_sample = Sample.objects.get(alias__iexact=str(pair[0]))
#         times_needed = pair[1]  # Number of times it appears in experiment
#         list_sample_wells = []
#
#         for part in vol_for_part:
#             sample_name, sample_direction, sample_sample_type, well_concentration, well_volume, sample_times_needed, \
#             times_available, vol_part_add, well_plate_name, well_name = part
#             if part_sample.name == sample_name:
#                 list_sample_wells.append(part)
#
#         if len(list_sample_wells) > 0:
#             list_source, alert = verify_wells_available_volume(list_sample_wells, part_sample, robot)
#
#             if len(alert) > 0:
#                 return None, alert
#             else:
#                 list_source_wells.extend(list_source)
#
#     return list_source_wells, alert


# def create_and_populate_sources_plate(found_list):
#     print('create_and_populate_sources_plate')
#     plates_in = parser.create_source_plates_from_foundlist(found_list)
#     plates_in = parser.list_to_source_plates(found_list, plates_in)
#     return plates_in


def get_count_unique_vol_list(count_unique_list, part_vol_list, dispenser_parameters):
    count_unique_vol_list = []
    for part in count_unique_list:
        part_name = part[0]
        part_count = part[1]
        part_sample = Sample.objects.get(alias__iexact=str(part[0]))
        if part_sample.sample_type == 'Primer':
            div = 1000
        else:
            div = 1
        volume = calc.total_volume_part_list(part_name, part_vol_list, div, dispenser_parameters)
        count_unique_vol_list.append([part_name, volume, part_count])
    return count_unique_vol_list


def get_count_unique_list(unique_list, lists_parts):
    count_unique_list = []
    for part in unique_list:
        count = calc.num_times_part(part, lists_parts)
        count_unique_list.append([part, count])
    return count_unique_list


def get_list_no_repetition(lists_parts):
    unique_list = []
    for lista in lists_parts:
        for part in lista:
                if add_on_list(unique_list, part):
                    unique_list.append(part)
    return unique_list


def check_lists_size(lists_parts, lists_volume):
    alert = []
    part_vol_list = []
    if len(lists_parts) != len(lists_volume):
        alert.append('The number of parts and volume do not match')
        return alert, None
    else:
        for set_parts, set_volume in itertools.zip_longest(lists_parts, lists_volume, fillvalue=None):
            part_vol = []
            for part, volume in itertools.zip_longest(set_parts, set_volume, fillvalue=None):
                part_vol.append([part, volume])
                if part is None or volume is None:
                    alert.append('The number of parts and volume do not match')
                    return alert, None
            part_vol_list.append(part_vol)
    return None, part_vol_list


def get_sets_in_filepath(reader):
    lists_parts = []
    '''For each line in file get the list'''
    for line in reader:
        set = []
        parts = line.strip("\n").split(',')
        '''List of parts'''
        for part in parts:
            part = part.replace(", ", ",")
            part = part.replace('"', "")
            set.append(part)
        '''Create the single list of parts'''
        lists_parts.append(list(set))
    return lists_parts


def run(path, filename_p, filename_v, dispenser_parameters, out_num_well, pattern, user, scriptname):
    total_alert = []
    name_machine, min_vol, res_vol, dead_vol = dispenser_parameters
    robot = machine.Machine(name_machine, min_vol, res_vol, dead_vol)

    '''Create read files'''
    filein_parts = file.verify(path + "/" + filename_p)
    filein_volume = file.verify(path + "/" + filename_v)

    '''Create write files'''
    db_robot_name = str(robot.name) + "_" + str(os.path.splitext(filename_p)[0]) + '.csv'
    file_robot = file.create(path + "/docs/" + db_robot_name, 'w')
    robot_csv = file.create_writer_csv(file_robot)

    '''Create combinations'''
    lists_parts = get_sets_in_filepath(filein_parts)
    lists_volume = get_sets_in_filepath(filein_volume)
    # print(lists_parts)

    '''Check if the parts and volume files match size'''
    alert, part_vol_list = check_lists_size(lists_parts, lists_volume)
    if alert is not None:
        return alert, None

    '''Get unique samples - no repetition'''
    unique_list = get_list_no_repetition(lists_parts)
    # print(unique_list)

    '''Verify how many times it appears'''
    count_unique_list = get_count_unique_list(unique_list, lists_parts)
    # print(count_unique_list)

    count_unique_vol_list = get_count_unique_vol_list(count_unique_list, part_vol_list, dispenser_parameters)
    # print(count_unique_vol_list)

    '''Verify the parts on database'''
    found_list, missing_list = parser.find_samples_database(unique_list)
    # print(found_list)

    if len(missing_list) > 0:
        for item in missing_list:
            total_alert.append('Missing info for part: ' + str(item))
        return total_alert, None

    else:
        '''Calculate the part volumes'''
        # vol_for_part = calc_part_volumes_in_plate(count_unique_list, dispenser_parameters)
        list_source_wells, alert = check_sample_volume_plate(count_unique_vol_list, dispenser_parameters)
        if alert is not None:
            return alert, None

        else:
            '''Create a destination plates'''
            plates_out = create_destination_plates(lists_parts, out_num_well)

            '''Populate plate'''
            plates_out, out_dispenser, out_master_mix, out_water, alert = \
                populate_destination_plates(plates_out, list_source_wells, lists_parts, lists_volume, found_list,
                                            pattern)
            '''Robot Dispenser parts'''
            file.set_echo_header(robot_csv)
            file.write_dispenser_echo(out_dispenser, robot_csv)

    db_robot = db.save_file(db_robot_name, scriptname, user)
    return total_alert, db_robot

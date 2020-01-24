import os, itertools

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


def add_on_list(lista, item):
    for i in range(0, len(lista)):
        if lista[i] == item:
            return False
    return True


def get_count_unique_vol_list(count_unique_list, part_vol_list, dispenser_parameters):
    alert = []
    count_unique_vol_list = []
    for part in count_unique_list:
        part_name = part[0]
        part_count = part[1]
        try:
            part_sample = Sample.objects.get(alias__iexact=str(part[0]))
            if part_sample.sample_type == 'Primer':
                div = 1000
            else:
                div = 1
            volume = calc.total_volume_part_list(part_name, part_vol_list, div, dispenser_parameters)
            count_unique_vol_list.append([part_name, volume, part_count])
        except:
            alert.append('An error was found. Check if the Alias ' + str(part_name) + ' is duplicated in the database.')
            return alert, None
    return None, count_unique_vol_list


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
    lists_volume = []
    '''For each line in file get the list'''
    for line in reader:
        set_sample = []
        set_volume = []
        splitline = line.strip("\n").split(',,')
        parts = splitline[0].split(',')
        volumes = splitline[1].split(',')
        '''List of parts'''
        for part in parts:
            part = part.replace(", ", ",")
            part = part.replace('"', "")
            set_sample.append(part)
        for volume in volumes:
            volume = volume.replace(", ", ",")
            volume = volume.replace('"', "")
            set_volume.append(volume)
        '''Create the single list of parts'''
        lists_parts.append(list(set_sample))
        lists_volume.append(list(set_volume))
    return lists_parts, lists_volume


def run(path, filename_p, plate_content, dispenser_parameters, out_num_well, pattern, user, scriptname):
    total_alert = []
    name_machine, min_vol, res_vol, dead_vol = dispenser_parameters
    robot = machine.Machine(name_machine, min_vol, res_vol, dead_vol)

    '''Create read files'''
    filein_parts = file.verify(path + "/" + filename_p)

    '''Create write files'''
    db_robot_name = str(robot.name) + "_" + str(os.path.splitext(filename_p)[0]) + '.csv'
    file_robot = file.create(path + "/docs/" + db_robot_name, 'w')
    robot_csv = file.create_writer_csv(file_robot)

    '''Create combinations'''
    lists_parts, lists_volume = get_sets_in_filepath(filein_parts)

    '''Check if the parts and volume files match size'''
    alert, part_vol_list = check_lists_size(lists_parts, lists_volume)
    if alert is not None:
        return alert, None

    '''Get unique samples - no repetition'''
    unique_list = get_list_no_repetition(lists_parts)

    '''Verify how many times it appears'''
    count_unique_list = get_count_unique_list(unique_list, lists_parts)

    alert, count_unique_vol_list = get_count_unique_vol_list(count_unique_list, part_vol_list, dispenser_parameters)
    if alert is not None:
        return alert, None

    '''Verify the parts on database'''
    found_list, missing_list = parser.find_samples_database(unique_list, plate_content)

    if len(missing_list) > 0:
        for item in missing_list:
            total_alert.append('Missing info for part: ' + str(item))
        return total_alert, None

    else:
        '''Calculate the part volumes'''
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

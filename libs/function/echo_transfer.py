import os, itertools

from libs.biofoundry import db
from libs.misc import file, calc, parser
from libs.container import plate, machine
from db.models import Plate, Well, Sample, Project


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


def get_plate_with_empty_well_removed_outerwells(destination_plates, pattern):
    if pattern == BY_ROW:
        for p in range(0, len(destination_plates)):
            if destination_plates[p].get_empty_in_well_by_row() is not None:
                i, j = destination_plates[p].get_empty_in_well_by_row()
                return p, i, j
    else:
        for p in range(0, len(destination_plates)):
            if destination_plates[p].get_empty_in_well_by_row() is not None:
                i, j = destination_plates[p].get_empty_in_well_by_col()
                return p, i, j


def populate_destination_plates(plates_out, list_source_wells, lists_parts, lists_volume, found_list, pattern, num_removed_wells):
    alert = []
    out_dispenser = []
    out_master_mix = []
    out_water = []
    for set_p, set_v in zip(lists_parts, lists_volume):
        if num_removed_wells == 0:
            p, i, j = get_plate_with_empty_well(plates_out, pattern)
        else:
            p, i, j = get_plate_with_empty_well_removed_outerwells(plates_out, pattern)
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


def create_destination_plates(lists_parts, num_well_destination, remove_outer_wells):
    num = Plate.objects.latest('id').id
    plates_out = []
    num_receipts = 0
    for set in lists_parts:
        num_receipts += 1

    if remove_outer_wells is False:
        num_removed_wells = 0
        num_plates = calc.num_destination_plates(num_receipts, num_well_destination)
    else:
        rows, cols = calc.rows_columns(int(num_well_destination))
        num_removed_wells = 2*(cols+rows)-4
        num_remained_wells = num_well_destination - num_removed_wells
        num_plates = calc.num_destination_plates(num_receipts, num_remained_wells)

    for i in range(0, num_plates):
        num = num + 1
        plates_out.append(create_plate(num_well_destination, 'GF' + '{0:05}'.format(num)))

    return plates_out, num_removed_wells


def get_count_unique_vol_list(count_unique_list, part_vol_list, dispenser_parameters):
    alert = []
    count_unique_vol_list = []
    for part in count_unique_list:
        part_name = part[0]
        part_count = part[1]
        try:
            part_sample = Sample.objects.get(alias__iexact=str(part[0]))
            div = 1000
            volume = calc.total_volume_part_list(part_name, part_vol_list, div, dispenser_parameters)
            count_unique_vol_list.append([part_name, volume, part_count])
        except:
            alert.append('An error was found. Check if the Alias ' + str(part_name) + ' is duplicated in the database.')
            return alert, None
    return None, count_unique_vol_list


def check_sample_volume_plate(count_unique_vol_list, dispenser_parameters):
    total_vol_parts = []
    for pair in count_unique_vol_list:
        print(pair)
        vector, alert = calc_part_volumes_in_plate(pair, dispenser_parameters)
        if vector is not None:
            total_vol_parts.extend(vector)
        else:
            return None, alert
    return total_vol_parts, None


def find_samples_database(unique_list, database, db_reader):
    ''' Verify parts in database '''
    found_list = []
    missing_list = []
    for part in unique_list:
        found = False
        database.seek(0)
        for line in db_reader:
            part_indb, part_type, part_length, part_conc, part_vol, source_plate, source_well, num_well = line
            if part == part_indb and float(part_vol) > 0:
                found = True
                # print(part_indb, source_plate, source_well)
                found_list.append(line)
        if found is False:
            # print(part + ' is missing in database.')
            missing_list.append(part)
    return found_list, missing_list


def create_and_populate_sources_plate(db_reader, database):
    database.seek(0)
    plates_in = parser.create_source_plates_from_csv(db_reader)
    database.seek(0)
    plates_in = parser.csv_to_source_plates(db_reader, plates_in)
    return plates_in


def calc_part_volumes_in_plate(count_unique_list, plates_in, dispenser_parameters):
    machine, min_vol, res_vol, dead_vol = dispenser_parameters
    total_vol_parts = []

    for pair in count_unique_list:
        part_name = pair[0]
        count = pair[1]  # Number of times it appears in experiment

        for plate_in in plates_in:
            list_wells = plate_in.get_samples_well(part_name)
            while list_wells:
                try:
                    wellD = next(list_wells)

                    for sample in wellD.samples:
                        if sample.name == part_name:
                            # print(sample.name, sample.type, sample.length, sample.concentration, sample.volume)
                            '''fmol -> ng  of the part to give 80 or 40 fmol of that part'''
                            fmol, concent_fmol = calc.fmol(sample.type, sample.length, bb_fmol, part_fmol)

                            '''Volume of part to get the selected fmol in ng '''
                            vol_part_add = float(fmol) / float(sample.concentration)
                            # print(vol_part_add)

                            '''Rounding the part volume according to machine resolution'''
                            vol_part_add = calc.round_at(vol_part_add, res_vol)
                            # print(vol_part_add)

                            '''Minimal dispense volume'''
                            vol_part_add = max(vol_part_add, min_vol)
                            # print(vol_part_add)

                            total_vol_parts.append([sample.name, sample.type, sample.length, sample.concentration, sample.volume, count, vol_part_add, plate_in.name, wellD.name])

                except StopIteration:
                    break
    return total_vol_parts


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
            div = 1000
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


def run(path, filename, database, dispenser_parameters, dest_plate_parameters, user, scriptname):
    total_alert = []
    name_machine, min_vol, res_vol, dead_vol = dispenser_parameters
    num_well_destination, pattern, remove_outer_wells = dest_plate_parameters
    robot = machine.Machine(name_machine, min_vol, res_vol, dead_vol)

    '''Create read files'''
    filein = file.verify(path + "/" + filename)
    database = file.verify(path + "/" + database)
    db_reader = file.create_reader_csv(database)

    '''Create write files'''
    db_robot_name = str(robot.name) + "_" + str(os.path.splitext(filename)[0]) + '.csv'
    file_robot = file.create(path + "/docs/" + db_robot_name, 'w')
    robot_csv = file.create_writer_csv(file_robot)

    '''Create combinations'''
    lists_parts, lists_volume = get_sets_in_filepath(filein)
    print(lists_parts, lists_volume)

    '''Check if the parts and volume files match size'''
    alert, part_vol_list = check_lists_size(lists_parts, lists_volume)
    print(part_vol_list)

    if alert is not None:
        total_alert.append(alert)
        return total_alert, None

    '''Get unique samples - no repetition'''
    unique_list = get_list_no_repetition(lists_parts)

    '''Verify how many times it appears'''
    count_unique_list = get_count_unique_list(unique_list, lists_parts)

    """Verify the parts on database"""
    found_list, missing_list = find_samples_database(unique_list, database, db_reader)
    # print(found_list)

    if len(missing_list) > 0:
        for item in missing_list:
            total_alert.append('Alert for the missing parts: ' + str(item))
        return total_alert, None

    else:
        """Create and Populate Source Plates"""
        plates_in = create_and_populate_sources_plate(db_reader, database)

        """Calculate the part volumes"""
        vol_for_part = calc_part_volumes_in_plate(count_unique_list, plates_in, dispenser_parameters)

        """Verify parts volume in source plate"""
        list_source_wells, list_part_low_vol, alert = verify_samples_volume(vol_for_part, count_unique_list, robot)
        if len(alert) > 0:
            for item in alert:
                total_alert.append(item)

        """Create entry list for destination plates"""
        list_destination_plate = create_entry_list_for_destination_plate(lists_parts, list_part_low_vol)

    #     else:
    #         '''Create a destination plates'''
    #         plates_out, num_removed_wells = create_destination_plates(lists_parts, num_well_destination, remove_outer_wells)
    #
    #         '''Populate plate'''
    #         plates_out, out_dispenser, out_master_mix, out_water, alert = \
    #             populate_destination_plates(plates_out, list_source_wells, lists_parts, lists_volume, found_list,
    #                                         pattern, num_removed_wells)
    #         '''Robot Dispenser parts'''
    #         file.set_echo_header(robot_csv)
    #         file.write_dispenser_echo(out_dispenser, robot_csv)
    #
    db_robot = db.save_file(db_robot_name, 'Echo Transfer', user)
    return total_alert, db_robot

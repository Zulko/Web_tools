from ..biofoundry import db
from ..misc import calc, file, parser
from ..container import plate, machine
import sys, os


# Dispense modo in plate
BY_ROW = 0
BY_COL = 1
MAX_VALUE = 999999


# def get_plate_with_empty_well(destination_plates):
#     for i in range(0, len(destination_plates)):
#         if destination_plates[i].get_empty_well_coord() is not None:
#             return i


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


def calc_part_volumes_in_plate(count_unique_list, plates_in, mix_parameters, dispenser_parameters):
    part_fmol, bb_fmol, total_vol, buffer, rest_enz, lig_enz, add_water = mix_parameters
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


def calc_part_volumes(count_unique_list, found_list, mix_parameters, dispenser_parameters):
    part_fmol, bb_fmol, total_vol, buffer, rest_enz, lig_enz = mix_parameters
    machine, min_vol, res_vol, dead_vol = dispenser_parameters

    total_vol_parts = []

    for pair in count_unique_list:
        part_name = pair[0]
        count = pair[1]  # Number of times it appears in experiment
        part_type, part_length, part_conc = get_part_info(found_list, part_name)
        # part_in_plate = get_part_in_plate(plates_in, part_name)

        '''fmol -> ng  of the part to give 80 or 40 fmol of that part'''
        fmol, concent_fmol = calc.fmol(part_type, part_length, bb_fmol, part_fmol)
        # print(part_name, part_conc, part_type, part_length)

        '''Volume of part to get the selected fmol in ng '''
        vol_part_add = float(fmol)/float(part_conc)
        # print(vol_part_add)

        '''Rounding the part volume according to machine resolution'''
        vol_part_add = calc.round_at(vol_part_add, res_vol)
        # print(vol_part_add)

        '''Minimal dispense volume'''
        vol_part_add = max(vol_part_add, min_vol)
        # print(vol_part_add)

        total_vol_parts.append([part_name, count, vol_part_add])

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


def get_list_no_repetition(lists_parts):
    unique_list = []
    for lista in lists_parts:
        for part in lista:
                if add_on_list(unique_list, part):
                    unique_list.append(part)
    return unique_list


def get_count_unique_list(unique_list, lists_parts):
    count_unique_list = []
    for part in unique_list:
        count = calc.num_times_part(part, lists_parts)
        count_unique_list.append([part, count])
    return count_unique_list


def verify_samples_volume(vol_for_part, count_unique_list, robot):
    alert = []
    '''Volume needed of parts for the experiment'''
    list_source_wells = []
    list_part_low_vol = []
    for pair in count_unique_list:
        found = False
        tot_times = 0
        part_info = []
        part_name = pair[0]
        times_needed = pair[1]  # Number of times it appears in experiment
        for part in vol_for_part:
            sample_name, sample_type, sample_length, sample_concentration, sample_volume, sample_times_needed, vol_part_add, plate_in_name, wellD_name = part
            if part_name == sample_name:
                '''Calculate how many 'vol_part_add' have in the total volume in one well'''
                available_vol = float(sample_volume) - robot.dead_vol
                '''total times per well'''
                times_available = int(available_vol/vol_part_add)
                '''total times in all database'''
                tot_times += times_available
                part_info.append(part)

                if int(sample_times_needed) <= times_available:
                    list_source_wells.append([sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, times_available, vol_part_add, plate_in_name, wellD_name])
                    break
        if int(tot_times) >= int(times_needed):
            for part in part_info:
                sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, vol_part_add, plate_in_name, wellD_name = part
                # Calculate how many 'vol_part_add' have in the total volume in one well
                available_vol = float(sample_volume) - robot.dead_vol
                # total times per well
                times_available = int(available_vol / vol_part_add)
                list_source_wells.append([sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, times_available, vol_part_add, plate_in_name, wellD_name])
        else:
            for part in part_info:
                sample_name, sample_type, sample_length, sample_concentration, sample_volume, times_needed, vol_part_add, plate_in_name, wellD_name = part
                total_vol_part = times_needed*vol_part_add
                # print('Not enough volume for sample: ' + str(part_name) + ' available: ' + str(sample_volume) + " need: " + str(round(total_vol_part,2)))
                alert.append(['Not enough volume for sample: ' + str(part_name) + ' available: ' + str(sample_volume) + " need: " + str(round(total_vol_part,2))])
                list_part_low_vol.append([sample_name, total_vol_part])

    return list_source_wells, list_part_low_vol, alert


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


def get_sets_in_filepath(reader):
    lists_parts = []
    ''' For each line in file get the list'''
    for line in reader:
        set = []
        parts = line.strip("\n").split(',')
        '''List of parts'''
        for part in parts:
            part = part.replace(" ", "")
            set.append(part)
        ''' Create the single list of parts'''
        lists_parts.append(list(set))
    return lists_parts


def create_and_populate_sources_plate(db_reader, database):
    database.seek(0)
    plates_in = parser.create_source_plates_from_csv(db_reader)
    database.seek(0)
    plates_in = parser.csv_to_source_plates(db_reader, plates_in)
    return plates_in


def run_moclo(path, filename, database, dispenser_parameters, mix_parameters, out_num_well, pattern, use_high_low_chip_mantis, user):
    total_alert = []
    name_machine, min_vol, res_vol, dead_vol = dispenser_parameters
    robot = machine.Machine(name_machine, min_vol, res_vol, dead_vol)
    part_fmol, bb_fmol, total_vol, per_buffer, per_rest_enz, per_lig_enz, add_water = mix_parameters

    ''' Create read files'''
    filein = file.verify(path + "/" + filename)
    database = file.verify(path + "/" + database)
    db_reader = file.create_reader_csv(database)

    ''' Create write files'''
    db_mantis_name = 'mantis_' + str(os.path.splitext(filename)[0]) + '.csv'
    db_robot_name = str(robot.name) + "_" + str(os.path.splitext(filename)[0]) + '.csv'
    file_mantis = file.create(path + "/docs/" + db_mantis_name, 'w')
    file_robot = file.create(path + "/docs/" + db_robot_name, 'w')
    mantis_csv = file.create_writer_csv(file_mantis)
    robot_csv = file.create_writer_csv(file_robot)

    """Create combinations"""
    lists_parts = get_sets_in_filepath(filein)
    # print(lists_parts)

    ''' Get unique samples - no repetition'''
    unique_list = get_list_no_repetition(lists_parts)
    # print(unique_list)

    ''' Verify how many times it appears'''
    count_unique_list = get_count_unique_list(unique_list, lists_parts)
    # print(count_unique_list)

    """Verify the parts on database"""
    found_list, missing_list = find_samples_database(unique_list, database, db_reader)
    # print(found_list)

    if len(missing_list) > 0:
        for item in missing_list:
            total_alert.append('Alert for the missing parts: ' + str(item))
        return total_alert, None, None, None, None

    else:
        """Create and Populate Source Plates"""
        plates_in = create_and_populate_sources_plate(db_reader, database)

        """Calculate the part volumes"""
        vol_for_part = calc_part_volumes_in_plate(count_unique_list, plates_in, mix_parameters, dispenser_parameters)
        # print(vol_for_part)

        """Verify parts volume in source plate"""
        list_source_wells, list_part_low_vol, alert = verify_samples_volume(vol_for_part, count_unique_list, robot)
        if len(alert) > 0:
            for item in alert:
                total_alert.append(item)

        """Create entry list for destination plates"""
        list_destination_plate = create_entry_list_for_destination_plate(lists_parts, list_part_low_vol)

        if len(list_destination_plate) > 0:
            """Create a destination plates"""
            plates_out = create_destination_plates(list_destination_plate, out_num_well)

            """Populate plate"""
            plates_out, out_dispenser, out_master_mix, out_water, alert = populate_destination_plates(plates_out, list_destination_plate, list_source_wells, mix_parameters, pattern)
            # file.write_plate_by_col(plates_out)

            """Mantis output file"""
            file.set_mantis_import_header(mantis_csv)
            min_water_vol = get_min_water_vol(out_water)

            # water to add in master mix, enzime
            mixer_recipe = calc_mixer_volumes(mix_parameters)
            buffer_vol, rest_enz_vol, lig_enz_vol, total_vol_buffer = mixer_recipe

            chip_mantis = []

            if add_water is True:
                ''' Add water in Master Mix and Remove from Water list'''
                out_master_mix, out_water = reajust_mixer_water_volumes(out_master_mix, out_water, min_water_vol)

                '''Master Mix recipe output'''
                mixer_recipe_title = ["Buffer", "Restriction Enzyme", "Ligase Enzyme", "Water", "Master Mix"]
                min_water_vol = round(min_water_vol, 2)
                total_vol_buffer += min_water_vol
                mixer_recipe = [round(buffer_vol, 2), round(rest_enz_vol, 2), round(lig_enz_vol, 2),
                                round(min_water_vol, 2), round(total_vol_buffer, 2)]
                mixer_recipe_zip = zip(mixer_recipe, mixer_recipe_title)

            else:
                mixer_recipe_title = ["Buffer", "Restriction Enzime", "Ligase Enzime", "Total Buffer"]
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

        else:
            return total_alert, None, None, None, None

    db_mantis = db.save_file(db_mantis_name, 'Moclo', user)
    db_robot = db.save_file(db_robot_name, 'Moclo', user)
    return total_alert, db_mantis, db_robot, mixer_recipe_zip, chip_mantis_zip

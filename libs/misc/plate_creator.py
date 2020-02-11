from django.db.models.functions import Substr, Cast
from django.db.models import IntegerField

from ..container import plate, machine
from db.models import Plate, Well
from libs.misc import parser, calc, file
from libs.biofoundry import db

import os, re, sys, csv, math, operator

BY_ROW = 0
BY_COL = 1


def create_and_populate_sources_plate(plates):
    plates_in = parser.create_source_plates_from_db(plates)
    plates_in = parser.db_plates_to_source_plates(plates, plates_in)
    return plates_in


def create_plate(num_wells, name):
    rows, cols = calc.rows_columns(int(num_wells))
    new_plate = plate.Plate(rows, cols, name)
    return new_plate


def is_empty_col(plate_in, wells_col):
    count_empty = 0
    for row in wells_col:
        try:
            well = Well.objects.get(plate__name=str(plate_in.name), name=str(row))
        except:
            count_empty +=1

    # All wells in this column are empty
    if count_empty == len(wells_col):
        return True
    # Some wells has samples
    else:
        return False


def create_destination_plates(plates, list_source_wells, num_dots, num_dest_id, num_well_destination, remove_outer_wells):
    plates_out = []

    count = 0
    for col in list_source_wells:
        for row in col:
            count +=1
    num_receipts = count

    # num_receipts = 0
    # for plate in plates:
    #     num_receipts += plate.num_well
    # num_receipts = num_receipts * num_dots
    # print('num_receipts: ' + str(num_receipts))
    num_removed_wells = 0

    if remove_outer_wells is False:
        num_plates = calc.num_destination_plates(num_receipts, num_well_destination)
        for i in range(0, num_plates):
            num_dest_id = num_dest_id + 1
            plates_out.append(create_plate(num_well_destination, 'GF' + '{0:05}'.format(num_dest_id)))
    else:
        rows, cols = calc.rows_columns(int(num_well_destination))
        num_removed_wells = 2 * (cols + rows) - 4
        num_remained_wells = num_well_destination - num_removed_wells
        num_plates = calc.num_destination_plates(num_receipts, num_remained_wells)
        for i in range(0, num_plates):
            num_dest_id = num_dest_id + 1
            plates_out.append(create_plate(num_well_destination, 'GF' + '{0:05}'.format(num_dest_id)))

    return plates_out, num_dest_id, num_removed_wells


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


def populate_destination_plates(plate_in, plates_out, list_source_wells, dot_vol, pattern, num_removed_wells):
    out_dispenser = []
    for col in list_source_wells:

        for row in col:
            if num_removed_wells == 0:
                p, i, j = get_plate_with_empty_well(plates_out, pattern)
            else:
                p, i, j = get_plate_with_empty_well_removed_outerwells(plates_out, pattern)

            try:
                well = Well.objects.get(plate__name=str(plate_in.name), name=str(row))

                for sample in well.samples.all():
                    plates_out[p].wells[i][j].samples.append(plate.Sample(sample.name, sample.sample_type, sample.length, well.concentration, well.volume))
                    out_dispenser.append([sample.name, sample.alias, sample.sample_type, well.plate.barcode, well.plate.name, well.name, dot_vol, plates_out[p].name, plates_out[p].name, plates_out[p].wells[i][j].name, plates_out[p].id])
            except:
                plates_out[p].wells[i][j].samples.append(
                    plate.Sample(None, None, None, None, None))

    return plates_out, out_dispenser


def run_dot_plate(path, plate_id, num_dots, dot_vol, num_well_destination, pattern, remove_outer_wells, user):
    plates = Plate.objects.filter(pk__in=plate_id)
    num_dest_id = Plate.objects.latest('id').id

    db_robot_name = str('echo') + "_" + str('dot-plating') + '.csv'
    file_robot = file.create(path + "/docs/" + db_robot_name, 'w')
    robot_csv = file.create_writer_csv(file_robot)
    out_dispenser = []

    '''Create sources plates'''
    plates_in = create_and_populate_sources_plate(plates)

    list_plates_wells = []
    for plate_in in plates_in:
        list_source_wells = []
        for j in range(0, plate_in.num_cols):
            wells_col = []
            for i in range(0, plate_in.num_rows):
                wells_col.append(plate_in.wells[i][j].name)

            '''Check if the column is empty'''
            if is_empty_col(plate_in, wells_col) is False:
                for d in range(0, num_dots):
                    list_source_wells.append(wells_col)
            else:
                list_source_wells.append(wells_col)
        plates_out, num_dest_id, num_removed_wells = create_destination_plates(plates, list_source_wells, num_dots, num_dest_id, num_well_destination, remove_outer_wells)
        plates_out, out_plate_dispenser = populate_destination_plates(plate_in, plates_out, list_source_wells, dot_vol, pattern, num_removed_wells)
        out_dispenser.extend(out_plate_dispenser)

    # ''' Robot Dispenser parts '''

    file.set_echo_header(robot_csv)
    file.write_dispenser_echo(out_dispenser, robot_csv)
    db_robot = db.save_file(db_robot_name, 'Dot_plating_db', user)
    file_robot.flush()
    file_robot.close()

    return db_robot

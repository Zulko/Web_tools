import os
from django.shortcuts import get_object_or_404

from ..misc import calc, file, parser
from ..container import plate, machine
from db.models import Plate, Well


def create_plate(num_wells, name):
    """
    Returns a Plate with number of wells and name
    :param num_wells: int number (96, 384)
    :param name: String of plate name
    :return: Plate
    """
    print(num_wells)
    rows, cols = calc.rows_columns(int(num_wells))
    new_plate = plate.Plate(rows, cols, name)
    return new_plate


def create_plate_on_database_old(path, file, num_well_destination, step):
    filein = open(path + '/docs/' + file.name, 'r')
    plates_out = []
    filein.readline()  # jump header
    for line in filein:
        found = False
        line = line.split(',')
        if len(line) == 12:
            '''Echo file used in Spotting Script'''
            source_id, source_plate, source_well, destination_plate_id, destination_plate_name, destination_well, \
            volume, source_row, source_col, destination_row, destination_col, plate_row = line

        else:
            '''Echo file used in PCR Script and Moclo Script'''
            part, source_plate, source_well, destination_plate_id, destination_plate_name, destination_well, volume = line
        if len(plates_out) == 0:
            if num_well_destination == 96:
                plate = Plate.create(destination_plate_name, 'Plate', 'Process', 12, 8, 96)
            else:
                plate = Plate.create(destination_plate_name, 'Plate', 'Process', 24, 16, 384)
            plates_out.append(plate)
        else:
            for plate_out in plates_out:
                if plate_out.name == destination_plate_name:
                    found = True
            if found is False:
                if num_well_destination == 96:
                    plate = Plate.create(destination_plate_name, 'Plate', 'Process', 12, 8, 96)
                else:
                    plate = Plate.create(destination_plate_name, 'Plate', 'Process', 24, 16, 384)
                plates_out.append(plate)
    return plates_out


def create_plate_on_database(path, file, num_well_destination, step):
    filein = open(path + '/docs/' + file.name, 'r')
    plates_out = []
    filein.readline()  # jump header
    for line in filein:
        found = False
        line = line.split(',')
        if len(line) == 12:
            '''Echo file used in Spotting Script'''
            source_id, source_plate, source_well, destination_plate_id, destination_plate_name, destination_well, \
            volume, source_row, source_col, destination_row, destination_col, plate_row = line

        else:
            '''Echo file used in PCR Script and Moclo Script'''
            part, source_plate, source_well, destination_plate_id, destination_plate_name, destination_well, volume = line

        if len(plates_out) == 0:
            if num_well_destination == 96:
                plate = Plate.create(destination_plate_name, 'Plate', 'Process', 12, 8, 96)
            else:
                plate = Plate.create(destination_plate_name, 'Plate', 'Process', 24, 16, 384)

            Well.create(name=destination_well, volume=volume, concentration=0, plate=plate,
                                   parent_well=None)
            plates_out.append(plate)
        else:
            for plate_out in plates_out:
                if plate_out.name == destination_plate_name:
                    Well.create(name=destination_well, volume=volume, concentration=0,
                                       plate=plate, parent_well=None)
                    found = True
            if found is False:
                if num_well_destination == 96:
                    plate = Plate.create(destination_plate_name, 'Plate', 'Process', 12, 8, 96)
                else:
                    plate = Plate.create(destination_plate_name, 'Plate', 'Process', 24, 16, 384)

                Well.create(name=destination_well, volume=volume, concentration=0, plate=plate,
                                  parent_well=None)
                plates_out.append(plate)
    return plates_out



def list_plate_from_database(path, file):
    filein = open(path +'/docs/' + file.name, 'r')
    plates_in = []
    filein.readline() # jump header
    for line in filein:
        found = False
        line = line.split(',')
        part, source_plate, source_well, destination_plate_id, destination_plate_name, destination_well, volume = line
        if len(plates_in) == 0:
            plate = get_object_or_404(Plate, name=source_plate)
            plates_in.append(plate)
        else:
            for plate_in in plates_in:
                if plate_in.name == source_plate:
                    found = True
            if found is False:
                plate = get_object_or_404(Plate, name=source_plate)
                plates_in.append(plate)
    return plates_in


def create_source_plates_from_foundlist(foundlist):
    """
    Returns a list of Source Plates got from filein
    :param list: found_list
    :return: list of Plates
    """
    plates_in = []
    if len(foundlist[0]) == 9:
        for list in foundlist:
            found = False
            samp_name, subsamp_name, primer_direc, samp_type, samp_conc, volume, plate_name, well_name, plate_num_well = list
            if plate_name != '':
                if len(plates_in) == 0:
                    plates_in.append(create_plate(plate_num_well, plate_name))
                else:
                    for i in range(0, len(plates_in)):
                        if plates_in[i].name == plate_name:
                            found = True
                    if found is False:
                        plates_in.append(create_plate(plate_num_well, plate_name))

    else:
        for part in foundlist:
            found = False
            samp_name, samp_type, samp_len, samp_conc, volume, plate_name, plate_well, plate_num_well = part
            if plate_name != '':
                if len(plates_in) == 0:
                    plates_in.append(create_plate(plate_num_well, plate_name))
                else:
                    for i in range(0, len(plates_in)):
                        if plates_in[i].name == plate_name:
                            found = True
                    if found is False:
                        plates_in.append(create_plate(plate_num_well, plate_name))

    return plates_in


def create_source_plates_from_csv(filein):
    """
    Returns a list of Source Plates got from filein
    :param filein: file
    :param in_well: integer number of wells
    :return: list of Plates
    """
    file.get_header(filein)
    plates_in = []
    for line in filein:
        found = False
        samp_name, samp_type, samp_len, samp_conc, volume, plate_name, plate_well, plate_num_well = line
        if plate_name != '':
            if len(plates_in) == 0:
                plates_in.append(create_plate(plate_num_well, plate_name))
            else:
                for i in range(0, len(plates_in)):
                    if plates_in[i].name == plate_name:
                        found = True
                if found is False:
                    plates_in.append(create_plate(plate_num_well, plate_name))
        else:
            print("Could not read file:", filein)

    return plates_in


def csv_to_source_plates(filein, plates):
    """
    Returns a populate Plate from file
    :param plates: List of Plates Sources
    :param filein: csv file
    :return: List of Plates Sources
    """
    file.get_header(filein)
    for line in filein:
        samp_name, type, samp_len, samp_conc, volume, plate_name, plate_well, num_well = line
        for i in range(0, len(plates)):
            if plates[i].name == plate_name:
                row, col = calc.wellname_to_coordinates(plate_well)
                plates[i].wells[row][col].samples.append(
                    plate.Sample(samp_name, type, samp_len, samp_conc, volume))
    return plates


def list_to_source_plates(foundlist, plates):
    if len(foundlist[0]) == 9:
        for list in foundlist:
            samp_name, subsamp_name, primer_direc, samp_type, samp_conc, volume, plate_name, well_name, plate_num_well = list
            for i in range(0, len(plates)):
                if plates[i].name == plate_name:
                    row, col = calc.wellname_to_coordinates(well_name)
                    plates[i].wells[row][col].samples.append(
                        plate.Sample(subsamp_name, samp_type, primer_direc, samp_conc, volume))


    else:
        for part in foundlist:
            samp_name, type, samp_len, samp_conc, volume, plate_name, plate_well, num_well = part
            for i in range(0, len(plates)):
                if plates[i].name == plate_name:
                    row, col = calc.wellname_to_coordinates(plate_well)
                    plates[i].wells[row][col].samples.append(
                        plate.Sample(samp_name, type, samp_len, samp_conc, volume))
    return plates
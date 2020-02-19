import os, decimal, re
from django.shortcuts import get_object_or_404

from ..misc import calc, file
from ..container import plate, machine
from db.models import Plate, Well, Sample


def create_plate(num_wells, name):
    """
    Returns a Plate with number of wells and name
    :param num_wells: int number (96, 384)
    :param name: String of plate name
    :return: Plate
    """
    rows, cols = calc.rows_columns(int(num_wells))
    new_plate = plate.Plate(rows, cols, name)
    return new_plate


def create_plate_on_database_old(path, file, num_well_destination, step):
    filein = open(path + '/docs/' + file.name, 'r')
    plates_out = []
    filein.readline()  # skip header
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


def fill_plates(plates_out, num_well_destination, destination_plate_name, destination_well, volume, step, sample):
    found = False

    num = int(re.search(r'\d+', destination_plate_name).group())
    destination_plate_name = \
        str(step.experiment.project.name) + '_E' + str(step.experiment.id) + '_' + str(step.name) + '_' + str(
            num_well_destination) + '_' + str(num)

    if len(plates_out) == 0:
        if num_well_destination == 96:
            plate = Plate.create(destination_plate_name, 'Plate', 'Process', 12, 8, 96)
        else:
            plate = Plate.create(destination_plate_name, 'Plate', 'Process', 24, 16, 384)
        try:
            well = Well.create(name=destination_well, volume=volume, concentration=0, plate=plate, parent_well=None)
            if sample is not None: well.samples.add(sample)
            well.plate.project.add(step.experiment.project)
            well.save()
        except:
            well = get_object_or_404(Well, plate=plate, name=destination_well)
            if sample is not None: well.samples.add(sample)
            well.volume = well.volume + decimal.Decimal(volume)
            well.save()
        plates_out.append(plate)
        return plates_out
    else:
        for plate_out in plates_out:
            if plate_out.name == destination_plate_name:
                try:
                    well = Well.create(name=destination_well, volume=volume, concentration=0,
                                       plate=plate_out, parent_well=None)
                    if sample is not None: well.samples.add(sample)
                    well.plate.project.add(step.experiment.project)
                    well.save()
                except:
                    well = get_object_or_404(Well, plate=plate_out, name=destination_well)
                    if sample is not None: well.samples.add(sample)
                    well.volume = well.volume + decimal.Decimal(volume)
                    well.save()
                found = True
        if found is False:
            if num_well_destination == 96:
                plate = Plate.create(destination_plate_name, 'Plate', 'Process', 12, 8, 96)
            else:
                plate = Plate.create(destination_plate_name, 'Plate', 'Process', 24, 16, 384)

            try:
                Well.create(name=destination_well, volume=volume, concentration=0, plate=plate,
                            parent_well=None)
            except:
                well = get_object_or_404(Well, plate=plate, name=destination_well)
                well.volume = well.volume + decimal.Decimal(volume)
                if sample is not None: well.samples.add(sample)
                well.save()
            plates_out.append(plate)
            return plates_out
    return plates_out


def create_plate_on_database(path, file, num_well_destination, step):
    filein = open(path + '/docs/' + file.name, 'r')
    plates_out = []
    filein.readline()  # jump header
    for line in filein:
        line = line.split(',')
        if len(line) == 12:
            '''Echo file used in Spotting Script'''
            source_id, source_plate, source_well, destination_plate_id, destination_plate_name, destination_well, \
            volume, source_row, source_col, destination_row, destination_col, plate_row = line
            volume = float(volume)/1000
            plates_out = fill_plates(
                plates_out, num_well_destination, destination_plate_name, destination_well, volume, step, None)

        else:
            '''Echo file used in PCR Script and Moclo Script'''
            part, source_plate, source_well, destination_plate_id, destination_plate_name, destination_well, volume = line
            sample = Sample.objects.get(name__exact=part)
            volume = float(volume)/1000
            plates_out = fill_plates(
                plates_out, num_well_destination, destination_plate_name, destination_well, volume, step, sample)
    # print(plates_out)
    return plates_out


def list_plate_from_database(path, file):
    filein = open(path + '/docs/' + file.name, 'r')
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
            samp_name, alias, samp_len, samp_direction, samp_type, samp_moclotype, samp_conc, volume, barcode, plate_name, plate_well, plate_num_well = part
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


def create_source_plates_from_db(plates):
    plates_in = []
    for plate in plates:
        plates_in.append(create_plate(int(plate.num_well), plate.name))

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
        # print(line)
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
            samp_name, alias, samp_len, samp_direction, samp_type, samp_moclotype, samp_conc, volume, barcode, plate_name, plate_well, plate_num_well = part
            for i in range(0, len(plates)):
                if plates[i].name == plate_name:
                    row, col = calc.wellname_to_coordinates(plate_well)
                    plates[i].wells[row][col].samples.append(
                        plate.Sample(alias, samp_moclotype, samp_len, samp_conc, volume))
    return plates


def db_plates_to_source_plates(platesdb, plates_in):
    for i in range(0, len(plates_in)):
        wells = Well.objects.filter(plate__name=plates_in[i].name)
        for well in wells:
            row, col = calc.wellname_to_coordinates(well.name)
            for sample in well.samples.all():
                plates_in[i].wells[row][col].samples.append(
                plate.Sample(sample.name, sample.sample_type, sample.direction, well.concentration, well.volume))

    return plates_in


def get_wells(part, plate_filters):
    plate_content, plate_project, plate_ids = plate_filters
    if len(plate_ids) < 1:
        wells = Well.objects.filter(
            samples__alias__exact=str(part),
            plate__contents__exact=str(plate_content),
            plate__project__id=plate_project)
    else:

        wells = Well.objects.filter(
            samples__alias__exact=str(part),
            plate__in=plate_ids)
    return wells


def is_foundlist_complete(unique_list, found_list):
    missing_list = []
    for part in unique_list:
        found = False
        for found_part in found_list:
            if part == found_part[1]:
                found = True
        if found == False:
            missing_list.append(part)
    return missing_list


def find_samples_database(unique_list, plate_filters):
    found_list = []
    missing_list = []

    for part in unique_list:
        wells = get_wells(part, plate_filters)
        if len(wells) > 0:
            for well in wells:
                samples = well.samples.all()
                if len(samples) == 1:
                    for sample in samples:
                        if well.volume > 0 and sample.alias == part and sample.sample_type is not None and well.active is True:
                            lista = [sample.name, sample.alias, sample.length, str(sample.direction),
                                     str(sample.sample_type), sample.moclo_type, float(well.concentration),
                                     float(well.volume), well.plate.name, well.name, int(well.plate.num_well)]
                            found_list.append(lista)
                        else:
                            missing_list.append(part)
                else:
                    missing_list.append(part)
        else:
            missing_list.append(part)
    missing_list = is_foundlist_complete(unique_list, found_list)
    return found_list, missing_list
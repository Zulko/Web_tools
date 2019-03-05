"""
# Library to deal with input and output files
"""


import os
import sys
import csv
import re

# DATABASE = "../input/database.csv"

# SEP = '\t'
SEP = ','


class colours:
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BLUE = '\033[34m'
    RED = '\033[31m'


def create(filename, mode):
    """Create a new file"""
    newfile = open(filename, mode)
    return newfile


def create_reader_CSV(filein):
    filein = csv.reader(filein)
    return filein


def create_writer_CSV(newfile):
    """Create a new file"""
    newfile = csv.writer(newfile, dialect='excel')
    return newfile


def get_extension(path):
    """Return the file extension"""
    filename, file_extension = os.path.splitext(path)
    return file_extension


def get_filename(path):
    """Return filename without extension"""
    filename, file_extension = os.path.splitext(path)
    return filename


def create_path(path):
    os.makedirs(path)


def verify_path(path):
    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path):
        create_path(dir_path)


def verify(path):
    """Verify if the file exist"""
    try:
        f = open(path, 'r')
        return f

    except IOError:
        print('File could not be opened.')
        sys.exit(0)


def get_header(filein):
    """Get the first line in file (header)"""
    header = next(filein, None)
    return header


def set_header(fileout):
    header = 'Source ID', 'Source Plate Name','Source Well','Destination ID','Destination Plate Name','Destination Well','Volume'
    fileout.writerow(header)


def set_biomek_header(fileout):
    header = 'Source ID', 'Source Plate Name','Source Well','Destination ID','Destination Plate Name','Destination Well','Volume',\
             'Source Row','Source Column','Destination Row','Destination Column','Plate+Row'
    fileout.writerow(header)


def set_worklist_header(fileout):
    header = 'header','Splate','Dplate','col'
    fileout.writerow(header)


def set_normal_header(fileout):
    header = 'Source ID','Description','DNA ID',\
             'DNA Plate BIOMEK','DNA Plate Well', 'Volume DNA', \
             'Diluent Plate BIOMEK','Diluent Plate Well', 'Volume Diluent',\
             'Destination Plate','Destination Well','Destination ID','Final Concentration'
    fileout.writerow(header)


def write_normal_result(fileout, result):

    for i in range(0, len(result)):
        part, source_id, source_plate_name, source_well_name, water_id, water_plate_name, water_plate_well, \
        dest_plate, dest_id, dest_well, final_concent, vol_sample, vol_water, error = result[i]

        row = source_id, '...', part, source_plate_name, source_well_name, vol_sample, water_plate_name, \
              water_plate_well, vol_water, dest_plate, dest_well, dest_id, final_concent

        if len(error) > 0:
            print(colours.RED + str(error) + colours.ENDC)
        else:
            fileout.writerow(row)


def write_by_col(source_plate, destination_plates, num_pattern, outfile, VOLUME):
    """
    Create a .csv file to be used in biomek
    :param source_plate: object from Plate Class
    :param destination_plates: a vector with of Plate Class that will receive the samples from source plate
    :param num_pattern: number of repetitions samples get from source plates
    :param outfile: A CSV file to be used in biomek with the choosed pattern
    with 1 source plate and num_pattern = 2, pattern = bycols, the output file will be like:
    Source Plate Name,Source Well,Destination Plate Name,Destination Well,Volume
    PlateS1,A1,PlateD1,A1,4
    PlateS1,A1,PlateD1,B1,4
    PlateS1,A2,PlateD1,C1,4
    PlateS1,A2,PlateD1,D1,4
    """
    source_wells = source_plate.iterR(num_pattern)
    for plateD in destination_plates:
        dest_wells = plateD.iterC(1)
        while source_wells and dest_wells:
            try:
                wellD = next(dest_wells)
                wellS = next(source_wells)
                result = source_plate.id, source_plate.name, wellS.name, plateD.id, plateD.name, wellD.name, VOLUME
                outfile.writerow(result)
            except StopIteration:
                break


def write_by_row(source_plate, destination_plates, num_pattern, outfile, VOLUME):
    """
    Create a .csv file to be used in biomek
    :param source_plate: source_plates: object from Plate Class
    :param destination_plates: a vector with of Plate Class that will receive the samples from source plate
    :param num_pattern: number of repetitions samples get from source plates
    :param outfile: A CSV file to be used in biomek with the choosed pattern
    with 1 source plate and num_pattern = 2, pattern = byrows, the output file will be like:
    Source Plate ID,Source Plate Name,Source Well,Destination Plate ID,Destination Plate Name,Destination Well,Volume
    IDPS1,PlateS1,A1,IDPD1,PlateD1,A1,4
    IDPS1,PlateS1,A1,IDPD1,PlateD1,A2,4
    IDPS1,PlateS1,A2,IDPD1,PlateD1,A3,4
    IDPS1,PlateS1,A2,IDPD1,PlateD1,A4,4
    """
    source_wells = source_plate.iterR(num_pattern)
    for plateD in destination_plates:
        dest_wells = plateD.iterR(1)
        while dest_wells:
            try:
                wellD = next(dest_wells)
                wellS = next(source_wells)
                result = source_plate.id, source_plate.name, wellS.name, plateD.id, plateD.name, wellD.name, VOLUME
                outfile.writerow(result)
            except StopIteration:
                break


def write_scol_dcol_by_spot(source_plate, destination_plates, num_pattern, outfile, VOLUME):
    """
    Create a .csv file to be used in biomek
    :param source_plate: source_plates: object from Plate Class
    :param destination_plates: a vector with of Plate Class that will receive the samples from source plate
    :param num_pattern: number of repetitions samples get from source plates
    :param outfile: A CSV file to be used in biomek with the choosed pattern
    with 1 source plate and num_pattern = 2, the output file will be like:
    Source Plate ID,Source Plate Name,Source Well,Destination Plate ID,Destination Plate Name,Destination Well,Volume
    IDPS1,PlateS1,A1,IDPD1,PlateD1,A1,4
    IDPS1,PlateS1,A1,IDPD1,PlateD1,A2,4
    IDPS1,PlateS1,B1,IDPD1,PlateD1,B1,4
    IDPS1,PlateS1,B1,IDPD1,PlateD1,B2,4
    """
    source_wells = source_plate.iterC(num_pattern)
    for plateD in destination_plates:
        dest_wells = plateD.iterRC_by_spot(num_pattern)
        while dest_wells:
            try:
                wellD = next(dest_wells)
                wellS = next(source_wells)
                result = source_plate.id, source_plate.name, wellS.name, plateD.id, plateD.name, wellD.name, VOLUME, \
                         wellS.name[0], re.findall('\d+', wellS.name)[0], wellD.name[0], re.findall('\d+', wellD.name)[0], source_plate.id
                outfile.writerow(result)
            except StopIteration:
                break




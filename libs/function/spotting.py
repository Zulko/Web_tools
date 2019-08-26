"""
Functions to create CSV files to be used in biomek

Source Plate Name,Source Well,Destination Plate Name,Destination Well,Volume
PlateS1,A1,PlateD1,A1,4
PlateS1,A1,PlateD1,B1,4
PlateS1,A2,PlateD1,C1,4
PlateS1,A2,PlateD1,D1,4
"""
from ..biofoundry import db
from ..misc import calc, file
from ..container import plate
import sys, os

MAX_PLATES = 12
VOLUME = 4
BY_ROW = 0
BY_COL = 1
BIOMEK = 2


def verify_entry(type, num):
    try:
        '''Verify if the numbers type is correct'''
        num = type(num)
    except ValueError:
        message = str(num) + ' is not a number'
        print(message)
        sys.exit()
    if num <= 0:
        message = 'the value needs to be greater than ' + str(num)
        print(message)
        sys.exit()
    else:
        return num



def generate_random_names(name, init, end):
    """
    Returns a vector with a main name + number
    :param name: string
    :param init: int number
    :param end: int number
    :return: a vector
    """
    names = []
    for i in range(init, end):
        names.append(str(name) + str(i))
    return names


def create_plate(num_wells, name):
    """
    Returns a named plate type 96 or 384 according to num_wells
    :param num_wells: int [96, 384]
    :param name: string
    :return: object from class Plate
    """
    rows, cols = calc.rows_columns(int(num_wells))
    new_plate = plate.Plate(rows, cols, name)
    return new_plate


def create_output_file(total_source, num_wells, total_destination, pattern):
    'TODO: Receive from html the plates names'
    """
    Create a random output file name, and plates names
    :param total_source: integer number
    :param total_destination: integer number
    :param pattern: integer number 0 -> BY_ROW or 1 -> BY_COL, New option
           BIOMEK = 2 (Outputs a CSV file efficient for that robot)
    """
    num_pattern = int(total_destination/total_source)
    '''Add the header'''
    if pattern == BY_ROW:
        file_path_out = 'media/docs/source_' + str(total_source) + '_' + str(num_pattern) + 'spot_byrow.csv'
        outfile = file.create(file_path_out, 'w')
        outcsv = file.create_writer_csv(outfile)
        file.verify(file_path_out)
        file.set_header(outcsv)
        ''' Create the source plates'''
        for i in range(0, total_source):
            plateS_num = i + 1
            source_name = 'Source_' + str(plateS_num)
            source_plate = create_plate(num_wells, source_name)
            destination_names = generate_random_names('Destination_', num_pattern*i+1, num_pattern*i+num_pattern+1)
            destination_plates = []
            for j in range(0, len(destination_names)):
                destination_plates.append(create_plate(num_wells, destination_names[j]))
            '''Call Function to write the CSV by rows'''
            file.write_by_row(source_plate, destination_plates, num_pattern, outcsv, VOLUME)
        outfile_name = os.path.basename(file_path_out)
        # print(file.colours.BOLD + 'Output File: ' + outfile_name + file.colours.BOLD)
        return outfile_name, file_path_out, None, None

    elif pattern == BY_COL:
        file_path_out = 'media/docs/source_' + str(total_source) + '_' + str(num_pattern) + 'spot_bycol.csv'
        outfile = file.create(file_path_out, 'w')
        outcsv = file.create_writer_csv(outfile)
        file.verify(file_path_out)
        file.set_header(outcsv)
        ''' Create the source plates'''
        for i in range(0, total_source):
            plateS_num = i + 1
            source_name = 'Source_' + str(plateS_num)
            source_plate = create_plate(num_wells, source_name)
            destination_names = generate_random_names('Destination_', num_pattern * i + 1, num_pattern * i + num_pattern + 1)
            destination_plates = []
            for j in range(0, len(destination_names)):
                destination_plates.append(create_plate(num_wells, destination_names[j]))
            '''Call Function to write the CSV by rows'''
            file.write_by_col(source_plate, destination_plates, num_pattern, outcsv, VOLUME)
        outfile_name = os.path.basename(file_path_out)
        # print(file.colours.BOLD + 'Output File: ' + outfile_name + file.colours.BOLD)
        return outfile_name, file_path_out, None, None

    else:
        file_path_out = 'media/docs/source_' + str(total_source) + '_' + str(num_pattern) + 'spot_biomek.csv'
        file_worklist_path_out = 'media/docs/source_' + str(total_source) + '_' + str(num_pattern) + 'spot_worklist.csv'
        outfile = file.create(file_path_out, 'w')
        out_worklist = file.create(file_worklist_path_out, 'w')
        file.verify(file_path_out)
        file.verify(file_worklist_path_out)
        outcsv = file.create_writer_csv(outfile)
        outcsv_worklist = file.create_writer_csv(out_worklist)
        file.set_biomek_header(outcsv)
        file.set_worklist_header(outcsv_worklist)
        ''' Create the source plates'''
        for i in range(0, total_source):
            plateS_num = i + 1
            source_name = 'Source_' + str(plateS_num)
            source_plate = create_plate(num_wells, source_name)
            destination_names = generate_random_names('Destination_', num_pattern * i + 1, num_pattern * i + num_pattern + 1)
            destination_plates = []
            for j in range(0, len(destination_names)):
                destination_plates.append(create_plate(num_wells, destination_names[j]))
            '''Call Function to write the CSV by rows'''
            file.write_scol_dcol_by_spot(source_plate, destination_plates, num_pattern, outcsv, VOLUME, outcsv_worklist)
        outfile_name = os.path.basename(file_path_out)
        outfile_worlistname = os.path.basename(file_worklist_path_out)
        # print(file.colours.BOLD + 'Output File: ' + outfile_name + '\tWorklist: ' + outfile_worlistname + file.colours.BOLD)
        return outfile_name, file_path_out, outfile_worlistname, file_worklist_path_out


def run_spotting(num_source_plates, num_wells, num_pattern, pattern, user):
    """
    Calls a function to create a output file
    The output file has the source plate and the distribution of the samples according to the num_pattern and pattern
    :param num_source_plates: int number
    :param num_pattern: int number
    :param pattern: 0 or 1
    """
    ver_num_source = verify_entry(int, num_source_plates)
    ver_pattern = verify_entry(int, num_pattern)
    total_destination = ver_num_source * ver_pattern
    total_plates = ver_num_source + total_destination
    if total_plates > MAX_PLATES:
        print('The total plates (%d) exceeds the biomek limit of %d' % (total_plates, MAX_PLATES))
        alert = 'The total number of plates is %d and exceeds the maximum number of plates (%d) in Biomek' % (total_plates, MAX_PLATES)
        return None, None, alert
    else:
        # print('The total plates in biomek is %d' % total_plates)
        # print('The total destination plate(s) is %d and total source plate(s) is %d' % (total_destination, ver_num_source))
        outfile_name, outfilepath, worklist_name, worklistpath = \
            create_output_file(ver_num_source, num_wells, total_destination, pattern)

        db_outfile = db.save_file(outfile_name, 'Spotting', user)
        db_worklist = db.save_file(worklist_name, 'Spotting', user)
        # print(db_worklist, db_outfile.file.url)

    # return outfile_name, worklist_name, None
    return db_outfile, db_worklist, None
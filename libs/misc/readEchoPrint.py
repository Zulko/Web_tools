#! usr/bin/python3.6
##
##
# Concordia Genome Foundry
# author: Flavia Araujo
# date: February 12th, 2020
# Function to read the xml files created by Echo 550
import os, sys, operator, csv
from datetime import timedelta, datetime
from xml.dom import minidom
import xml.etree.ElementTree as ET

from django.conf import settings


def create(filename, mode):
    """Create a new file"""
    newfile = open(filename, mode)
    return newfile


def create_writer_csv(newfile):
    """Create a new file"""
    newfile = csv.writer(newfile, dialect='excel')
    return newfile


def print_csv_files(filepath, files_output):
    count = 2
    for list_file in files_output:
        count +=1
        file = open(os.path.join(filepath, 'echo_' + str(count)) + '.csv', 'w')
        csv_file = csv.writer(file, dialect='excel')
        header = 'file', 'source_well', 'destination_well', 'actual_vol_transferred', 'volume_transferred'
        csv_file.writerow(header)

        sorted_list_file = sorted(list_file, key=operator.itemgetter(1))
        for well in sorted_list_file:
            csv_file.writerow(well)
        file.flush()
        file.close()


def list_group_files(files_skippedwells):
    '''Sort list of files by date'''
    sorted_files_skippedwells = sorted(files_skippedwells, key=operator.itemgetter(2))
    file, num_skippedwells, start_date = sorted_files_skippedwells[0]

    group_files_list = []
    actual_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f')
    count = 1
    for file_list in sorted_files_skippedwells:
        file, num_skippedwells, file_date = file_list
        obj_file_date = datetime.strptime(file_date, '%Y-%m-%d %H:%M:%S.%f')
        difference = obj_file_date - actual_date

        '''Check if the time between files less then 30min'''
        if difference.seconds < 1800:
            list = count, file, num_skippedwells, file_date
            group_files_list.append(list)
        else:
            count += 1
            list = count, file, num_skippedwells, file_date
            group_files_list.append(list)
        actual_date = obj_file_date

    return group_files_list


def print_skippedwells_list(filepath, group_files_list):
    actual_group = 1
    file_output = []
    files_output = []
    for xml in group_files_list:
        file_group = xml[0]
        xml_file = xml[1]
        num_skippedwells = int(xml[2])
        file_datetime = xml[3]

        if file_group == actual_group:
            xmldoc = minidom.parse(os.path.join(filepath, xml_file))

            w = xmldoc.getElementsByTagName('w')
            skippedwells = xmldoc.getElementsByTagName('skippedwells')
            printmap = xmldoc.getElementsByTagName('printmap')
            transfer = xmldoc.getElementsByTagName('transfer')

            date = transfer[0].attributes['date'].value
            num_skippedwells = int(skippedwells[0].attributes['total'].value)
            num_printmapwells = int(printmap[0].attributes['total'].value)

            for i in range(0 + num_printmapwells, num_skippedwells + num_printmapwells):
                source_well = w[i].attributes['n'].value
                destination_well = w[i].attributes['dn'].value
                actual_vol_transferred = w[i].attributes['avt'].value
                volume_transferred = w[i].attributes['vt'].value
                file_output.append([xml_file, source_well, destination_well, actual_vol_transferred, volume_transferred])
        else:
            actual_group = file_group
            files_output.append(file_output)
            file_output = []
            xmldoc = minidom.parse(os.path.join(filepath, xml_file))

            w = xmldoc.getElementsByTagName('w')
            skippedwells = xmldoc.getElementsByTagName('skippedwells')
            printmap = xmldoc.getElementsByTagName('printmap')
            transfer = xmldoc.getElementsByTagName('transfer')

            date = transfer[0].attributes['date'].value
            num_skippedwells = int(skippedwells[0].attributes['total'].value)
            num_printmapwells = int(printmap[0].attributes['total'].value)

            for i in range(0 + num_printmapwells, num_skippedwells + num_printmapwells):
                source_well = w[i].attributes['n'].value
                destination_well = w[i].attributes['dn'].value
                actual_vol_transferred = w[i].attributes['avt'].value
                volume_transferred = w[i].attributes['vt'].value
                file_output.append([xml_file, source_well, destination_well, actual_vol_transferred, volume_transferred])
    files_output.append(file_output)
    return files_output


def check_barcode_skippedwells(filepath, xml_files, barcode):
    today = datetime.now()
    files_skippedwells = []
    empty_files = []
    for xml in xml_files:
        try:
            xmldoc = minidom.parse(os.path.join(filepath, xml))

            skippedwells = xmldoc.getElementsByTagName('skippedwells')
            platebarcode = xmldoc.getElementsByTagName('plate')
            transfer = xmldoc.getElementsByTagName('transfer')

            num_skippedwells = int(skippedwells[0].attributes['total'].value)
            plate_barcode = platebarcode[0].attributes['barcode'].value
            date = transfer[0].attributes['date'].value

            obj_file_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
            dif_time = today - obj_file_date

            if num_skippedwells > 0 and barcode == plate_barcode and dif_time.days < 15:
                files_skippedwells.append([xml, num_skippedwells, date])
        except:
            empty_files.append(xml)
    return files_skippedwells


def get_xml_files(path):
    list_all_files = os.listdir(path)
    filtered_files = []
    for file in list_all_files:
        if file.endswith(".xml") and 'PrintResult' in file:
            filtered_files.append(file)
    return filtered_files


def main(argv):
    if len(sys.argv) > 0:
        # barcode = str(sys.argv[1])
        barcode = 'GF00007'
        filepath = os.path.join(settings.MEDIA_ROOT, 'xml')
        '''Get all xml files with Print Result'''
        xml_files = get_xml_files(filepath)

        '''Filter the files created today with skipped wells > 0 and the barcode'''
        if len(xml_files) > 0:
            files_skippedwells = check_barcode_skippedwells(filepath, xml_files, barcode)

            if len(files_skippedwells) > 0:
                group_files_list = list_group_files(files_skippedwells)
                files_output = print_skippedwells_list(filepath, group_files_list)
                print_csv_files(filepath, files_output)

            else:
                print(str(barcode) + ' not found in .xml files')
                sys.exit(0)

        else:
            print('.xml files not found')
            sys.exit(0)
    else:
        print('Error:Missing barcode >>python readEchoPrint.py <barcode>')
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
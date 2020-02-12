#! usr/bin/python3.6
##
##
# Concordia Genome Foundry
# author: Flavia Araujo
# date: February 12th, 2020
# Function to read the xml files created by Echo 550
import os
from xml.dom import minidom

from django.conf import settings


def print_skippedwells_list(filepath, files_skippedwells):
    for xml in files_skippedwells:
        xml_file = xml[0]
        num_skippedwells = int(xml[1])
        xmldoc = minidom.parse(os.path.join(filepath, xml_file))
        w = xmldoc.getElementsByTagName('w')
        print(xml_file)
        print('source_well', 'destination_well', 'actual_vol_transferred', 'volume_transferred')
        print(num_skippedwells)
        for i in range(0, num_skippedwells):
            source_well = w[i].attributes['n'].value
            destination_well = w[i].attributes['dn'].value
            actual_vol_transferred = w[i].attributes['avt'].value
            volume_transferred = w[i].attributes['vt'].value
            print(source_well, destination_well, actual_vol_transferred, volume_transferred)


def check_skippedwells(filepath, xml_files):
    files_skippedwells = []
    for xml in xml_files:
        xmldoc = minidom.parse(os.path.join(filepath, xml))
        skippedwells = xmldoc.getElementsByTagName('skippedwells')
        num_skippedwells = int(skippedwells[0].attributes['total'].value)
        if num_skippedwells > 0:
            files_skippedwells.append([xml,num_skippedwells])
    return files_skippedwells


def get_xml_files(path):
    list_all_files = os.listdir(path)
    filtered_files = []
    for file in list_all_files:
        if file.endswith(".xml") and 'PrintResult' in file:
            filtered_files.append(file)
    return filtered_files


def main():
    filepath = os.path.join(settings.MEDIA_ROOT, "xml")
    xml_files = get_xml_files(filepath)
    print(xml_files)

    if len(xml_files) > 0:
        files_skippedwells = check_skippedwells(filepath, xml_files)
        print(files_skippedwells)
        print_skippedwells_list(filepath, files_skippedwells)

    else:
        print('.xml files not found')


if __name__ == '__main__':
    main()
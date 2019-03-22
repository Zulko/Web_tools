from ..misc import calc, file, parser
from ..container import plate, machine


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
                    plate.Sample(samp_name, type, samp_len, samp_conc, int(volume)))
    return plates
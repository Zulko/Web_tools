"""
# File to calculate the normalization of samples and create a csv file to be used on BIOMEK
"""

from ..container import plate
from ..misc import file, calc
import os


def verify_sample_volume(volume_needed, volume_available):
    """
    Returns the minimal sample volume needed if available
    :param volume_needed:
    :param volume_available:
    :return:
    """
    ''' Verifies if the volume needed is available'''
    if volume_needed > volume_available:
        return None
    else:
        # biomek cant deal with liquids below 4ul
        ''' Verifies if the volume needed is bigger then Biomek minimal volume'''
        if volume_needed < plate.Sample.MIN_VOL:
            #Set the needed volume to minimal
            if volume_available >= plate.Sample.MIN_VOL:
                volume_needed = plate.Sample.MIN_VOL
                return volume_needed
            else:
                # print('Not enough sample')
                return None
        #volume_needed less than available and greater or equal to 4ul
        else:
            return volume_needed


def calc_normalization_from_plate(sample, plate_in, plate_water, i, j):
    """
    Returns a list with info about the volume of the sample and water to normalize
    :param sample: object from plate Sample
    :param plate_in: object Plate
    :param plate_water: Plate
    :param i: integer
    :param j: integer
    :return: list r_norm = [part, plate_name, well_name, fmol, vol_sample, vol_water, message]
    """
    fmol, final_concent = calc.fmol(sample.get_length(), sample.get_concentration())
    dilut_factor = calc.dilution_factor(fmol, sample.get_concentration())

    '''Verify the total sample volume available'''
    sample_vol_available = sample.get_volume()

    '''Calculate the sample volume to get at least 35ul in total volume'''
    sample_vol_needed = calc.sample_volume(dilut_factor, plate.Well.MIN_VOL)
    sample_vol_verified = verify_sample_volume(sample_vol_needed, sample_vol_available)

    if sample_vol_verified is None:
        message = 'Sample %s: volume needed %s / available volume %s.' % \
                  (sample.name, sample_vol_needed, sample_vol_available)
        r_norm = [sample.name, plate_in.id, plate_in.name, plate_in.wells[i][j].name, plate_water.id, plate_water.name,
                  plate_water.wells[i][j].name, '', '', '', final_concent, '', '', message]
        return r_norm

    else:
        ''' Calculate total volume'''
        total_volume = calc.total_volume(sample_vol_verified, dilut_factor)
        if total_volume > plate.Well.MAX_VOL:
            message = 'The total volume %d exceeds the well limit.' % total_volume
            r_norm = [sample.name, plate_in.id, plate_in.name, plate_in.wells[i][j].name, plate_water.id, plate_water.name,
                      plate_water.wells[i][j].name, '', '', '', final_concent, '', '', message]
            return r_norm

        else:
            '''Calculate water volume'''
            water_vol_needed = calc.water_volume(total_volume, sample_vol_needed)

            if plate.Sample.MIN_VOL > water_vol_needed > 0:
                ''' the water volume is too low'''
                message = 'The total volume of water %dul to dilute the sample %s is too low.' % (water_vol_needed, sample.name)
                r_norm = [sample.name, plate_in.id, plate_in.name, plate_in.wells[i][j].name, plate_water.id, plate_water.name,
                          plate_water.wells[i][j].name, '', '', '',  final_concent, '', '', message]
                return r_norm
            else:
                if water_vol_needed < 0:
                    ''' the sample concentration is too low'''
                    message = 'The sample %s concentration %sng/ul is too low to be used.' \
                              % (sample.name, sample.get_concentration())
                    r_norm = [sample.name, plate_in.id, plate_in.name, plate_in.wells[i][j].name, plate_water.id, plate_water.name,
                              plate_water.wells[i][j].name, '', '', '', final_concent, '', '', message]
                    return r_norm
                else:
                    r_norm = [sample.name, plate_in.id, plate_in.name, plate_in.wells[i][j].name, plate_water.id, plate_water.name,
                              plate_water.wells[i][j].name, '', '', '', final_concent, sample_vol_verified, water_vol_needed, '']
                    return r_norm


def populate_plates_sample(plates_in, filein):
    """
    Returns a populate Plate from file
    :param plates_in: List of Plates Sources
    :param filein: csv file
    :return: List of Plates Sources
    """
    file.get_header(filein)
    for line in filein:
        samp_name, samp_len, samp_conc, volume, plate_name, plate_well = line
        for i in range(0, len(plates_in)):
            if plates_in[i].name == plate_name:
                row, col = calc.wellname_to_coordinates(plate_well)
                plates_in[i].wells[row][col].samples.append(plate.Sample(samp_name, samp_len, samp_conc, int(volume)))
    return plates_in


def populate_plates_water(plates_water):
    """
    Returns a populate water Plate
    :param plate_water: Plate
    :return: Plate
    """
    for k in range(0, len(plates_water)):
        for i in range(0, plates_water[k].num_rows):
            for j in range(0, plates_water[k].num_cols):
                plates_water[k].wells[i][j].name = 'A1'
                plates_water[k].wells[i][j].samples.append(plate.Sample('water', None, None, plate.Well.MAX_VOL))
    return plates_water


def get_plate_with_empty_well(destination_plates):
    for i in range(0, len(destination_plates)):
        if destination_plates[i].get_empty_well_coord() is not None:
            return i


def populate_plates_destination(destination_plates, norm_result):
    """
    Returns filled destination plate and result
    :param plate_out: object Plate: destination plate for normalized samples
    :param norm_result: a list with normalized results
    :return: Plate, list
    """
    for k in range(0, len(norm_result)):
        sample_name, plate_in_id, plate_in_name, plate_in_wells, plate_water_id, plate_water_name, \
        plate_water_wells, d_id, d_plate, d_well, final_concent, sample_vol_verified, \
        water_vol_needed, message = norm_result[k]
        # print(len(message))
        if len(message) == 0:
            # Get the plate and empty well on the dest_plate
            i = get_plate_with_empty_well(destination_plates)
            row, col = destination_plates[i].get_empty_well_coord()
            destination_plates[i].wells[row][col].samples.append(plate.Sample(sample_name, None, None, sample_vol_verified))
            destination_plates[i].wells[row][col].samples.append(plate.Sample('water', None, None, water_vol_needed))
            norm_result[k][7] = destination_plates[i].id
            norm_result[k][8] = destination_plates[i].name
            norm_result[k][9] = destination_plates[i].wells[row][col].name

    return destination_plates, norm_result


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


def create_source_plates(filein, in_well):
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
        samp_name, samp_len, samp_conc, volume, plate_name, plate_well = line
        if plate_name != '':
            if len(plates_in) == 0:
                plates_in.append(create_plate(in_well, plate_name))
            else:
                for i in range(0, len(plates_in)):
                    if plates_in[i].name == plate_name:
                        found = True
                if found is False:
                    plates_in.append(create_plate(in_well, plate_name))
    return plates_in


def create_water_plates(plates_in, in_well):
    plates_water = []
    for i in range(0, len(plates_in)):
        plates_water.append(create_plate(in_well, 'Water'))
    return plates_water


def create_destination_plates(plates_in, in_well, out_well):
    plates_out = []
    if in_well == out_well:
        for i in range(0, len(plates_in)):
            plates_out.append(create_plate(out_well, 'Normalized_' + str(i+1)))
        return plates_out
    else:
        num_dest = calc.total_destination_plates(plates_in, in_well, out_well)
        for i in range(0, num_dest):
            plates_out.append(create_plate(out_well, 'Normalized_' + str(i+1)))
        return plates_out


def create_biomek_dilution_output(path, in_well, out_well):
    """
    Creates a CSV file to be used in Biomek with the volume of sample and water to normalize the sample
    :param path: input file with parts information
    :param in_well: number of well of input plate
    :param out_well: number of well of output plate
    """
    filein = file.verify(path)
    reader_csv = file.create_reader_CSV(filein)
    fileout = file.create('biomek/output/dilution_' + str(os.path.basename(path)), 'w')
    writer_csv = file.create_writer_CSV(fileout)
    file.set_normal_header(writer_csv)

    """Create a platemap"""
    plates_in = create_source_plates(reader_csv, in_well)
    plates_water = create_water_plates(plates_in, in_well)
    plates_out = create_destination_plates(plates_in, in_well, out_well)

    """Populate the plate"""
    filein.seek(0)
    populate_plates_sample(plates_in, reader_csv)
    populate_plates_water(plates_water)
    norm_result = []

    """Calculate Normalization for all source plates"""
    for k in range(0, len(plates_in)):
        for i in range(0, plates_in[k].num_rows):
            for j in range(0, plates_in[k].num_cols):
                """Calculate the normalization parameters"""
                for sample in plates_in[k].wells[i][j].samples:
                    norm_result.append(calc_normalization_from_plate(sample, plates_in[k], plates_water[k], i, j))

    # TODO: Modification in Plate Source, Water and Destination for a List of Plates

    plates_out_filled, new_result = populate_plates_destination(plates_out, norm_result)
    # """Write the result in a CSV file"""

    file.write_normal_result(writer_csv, new_result)
    print(file.colours.BOLD + 'Output File: ' + fileout.name + file.colours.ENDC)
    filein.close()
    fileout.close()

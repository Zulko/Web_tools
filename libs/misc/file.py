"""
# Library to deal with input and output files
"""
import os, re, sys, csv, math

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


def create_reader_csv(filein):
    filein = csv.reader(filein)
    return filein


def create_writer_csv(newfile):
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


def set_echo_header(fileout):
    header = 'Part', 'Source Plate Name','Source Well','Destination ID','Destination Plate Name','Destination Well','Volume'
    fileout.writerow(header)


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


def set_mantis_header(fileout, out_num_well):
    if out_num_well == 96:
        plate_name = 'PT9-96-Assay.pd.txt'
    elif out_num_well == 384:
        plate_name = 'PT9-96-Assay.pd.txt'
    else:
        print('Choose a defined plate type')
        sys.exit()

    header = ['[ Version: 1 ]'],[plate_name],['Master_Mix'+'\t'+'\t'+'Normal'],['Well'+'\t'+'1']
    for line in header:
        fileout.writerow(line)


def set_mantis_import_header(fileout):
    header = 'well','volume','reagent'
    fileout.writerow(header)


def write_normal_result(fileout, result):
    alert = []
    for i in range(0, len(result)):
        part, source_id, source_plate_name, source_well_name, water_id, water_plate_name, water_plate_well, \
        dest_plate, dest_id, dest_well, final_concent, vol_sample, vol_water, error = result[i]

        row = source_id, '...', part, source_plate_name, source_well_name, vol_sample, water_plate_name, \
              water_plate_well, vol_water, dest_plate, dest_well, dest_id, final_concent

        if len(error) > 0:
            alert.append(error)
            print(colours.RED + str(error) + colours.ENDC)
        else:
            fileout.writerow(row)
    return alert


def write_plate_by_col(destination_plates):
    for plateD in destination_plates:
        dest_wells = plateD.iterC(1)
        while dest_wells:
            try:
                wellD = next(dest_wells)
                # result = source_plate.id, source_plate.name, wellS.name, plateD.id, plateD.name, wellD.name, VOLUME
                result = plateD.id, plateD.name, wellD.name, wellD.samples
                print(result)
            except StopIteration:
                break


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


def write_scol_dcol_by_spot(source_plate, destination_plates, num_pattern, outfile, VOLUME, out_worklist):
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
    worklist_header = -1
    source_wells = source_plate.iterC(num_pattern)
    for plateD in destination_plates:
        dest_wells = plateD.iterRC_by_spot(num_pattern)
        while dest_wells:
            try:
                wellD = next(dest_wells)
                wellS = next(source_wells)
                result = source_plate.id, source_plate.name, wellS.name, plateD.id, plateD.name, wellD.name, VOLUME, \
                         wellS.name[0], re.findall('\d+', wellS.name)[0], wellD.name[0], re.findall('\d+', wellD.name)[
                             0], re.findall('\d+', source_plate.name)[0]+re.findall('\d+', plateD.name)[0]+re.findall('\d+', wellS.name)[0]
                outfile.writerow(result)

                temp_work_header = re.findall('\d+', source_plate.name)[0] + re.findall('\d+', plateD.name)[0] + re.findall('\d+', wellS.name)[0]

                if temp_work_header != worklist_header:
                    worklist_header = temp_work_header
                    s_plate = re.findall('\d+', source_plate.name)[0]
                    d_plate = re.findall('\d+', plateD.name)[0]
                    col = re.findall('\d+', wellS.name)[0]
                    worklist_result = worklist_header, s_plate, d_plate, col
                    out_worklist.writerow(worklist_result)

            except StopIteration:
                break


def write_combinations(outfile, list_combinations):
    for list in list_combinations:
        for parts in list:
            for i in range(0, len(parts)-1):
                outfile.write(parts[i] + ",")
            outfile.write(parts[i+1] + "\n")
    outfile.close()


def write_dispenser_echo(dispenser_list, fileout):
    for part in dispenser_list:
        name, type_part, source_plate, source_well, part_vol, dest_plate, dest_well, dest_id = part
        vol_nl = part_vol * 1000
        round_vol = int(vol_nl)
        result = [name, source_plate, source_well, dest_id, dest_plate, dest_well, round_vol]
        fileout.writerow(result)


def write_dispenser_mantis(file_mantis, reagents):
    for part in reagents:
        name = part[0]
        volume = round(float(part[1]), 1)
        well = part[2]
        result = [well,volume,name]
        file_mantis.writerow(result)


def write_dispenser_mantis_in_low_high_chip(file_mantis, reagents):
    for part in reagents:
        name = part[0]
        volume = round(float(part[1]), 1)
        well = part[2]

        ''' Separate integer and decimal '''
        vol_dec, vol_int = math.modf(volume)
        vol_dec = round(float(vol_dec), 1)

        ''' Create different reagents '''
        name_dec = name + '_low'
        name_int = name + '_high'
        result1 = [well,vol_dec,name_dec]
        result2 = [well,vol_int,name_int]

        file_mantis.writerow(result2)
        file_mantis.writerow(result1)
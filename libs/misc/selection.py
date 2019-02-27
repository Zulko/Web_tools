"""
# File to manager the selection among the function for BIOMEK outputs
"""
#TODO: Remove Selection.py
import sys
from ..function import normalization as nb
from ..function import spotting as tb


def combinatorial_data():
    print('Under development')
    sys.exit()


def data_normalization():
    filepath = input('Inform the filepath (biomek/input/to_be_normalized.csv): ')
    in_num_well = input('Inform the number of wells in source plate: ')
    out_num_well = input('Inform the number of wells in destination plate: ')
    # filepath = 'biomek/input/database.csv'
    # in_num_well = '96'
    # out_num_well = '96'
    nb.create_biomek_dilution_output(filepath, int(in_num_well), int(out_num_well))


def template():
    num_source_plates = input('Inform the number of source plates: ')
    num_pattern = input('Inform the pattern [1, 2, 3, 4, 6 or 8]: ')
    pattern = input('Pattern by row -> 0 '
                    + 'Pattern by column -> 1: ')
    tb.verify_biomek_constraints(int(num_source_plates), int(num_pattern), int(pattern))


def function(choose):
    """
    Function to select the function in the system
    :param choose: int number
    """
    if choose == 0:
        '''Create CSV templates'''
        template()
    elif choose == 1:
        '''Create Normalization CSV File'''
        data_normalization()
    elif choose == 2:
        '''Create Combinatorial CSV File'''
        combinatorial_data()
    else:
        print('Invalid option')
        sys.exit()


def autoplay():
    """
    Autoplay script that helps to choose the function desired
    :return: number int
    """
    # print(file.colours.BLUE + "Biomek Script" + file.colours.ENDC)
    # print('Please choose one option:\n')
    choose = input('0 -> Create a CSV file template\n'
                   '1 -> Create a Normalization CSV file\n'
                   '2 -> Create a CSV file with combinatorial\n'
                   +'Choose > ')

    return int(choose)
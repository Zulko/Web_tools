"""
# File to manager the selection among the function for BIOMEK outputs
"""

import sys
from biomek.misc import file
from ..function import normalization_biomek as nb
from ..function import spotting as tb
from ..interface import interface


def combinatorial_data():
    print('Under development')
    sys.exit()


def data_normalization():
    filepath = input('Inform the filepath (biomek/input/database.csv): ')
    in_num_well = input('Inform the number of wells in source plate: ')
    out_num_well = input('Inform the number of wells in destination plate: ')
    # filepath = 'biomek/input/database.csv'
    # in_num_well = '96'
    # out_num_well = '96'
    nb.create_biomek_dilution_output(filepath, int(in_num_well), int(out_num_well))


def template():
    num_source_plates = input('Inform the number of source plates: ')
    num_pattern = input('Inform the pattern [1, 2, 3, 4, 6 or 8]: ')
    pattern = input('Pattern by row -> ' + file.colours.RED + '0 ' + file.colours.ENDC
                    + 'Pattern by column -> ' + file.colours.RED + '1' + file.colours.ENDC + ': ')
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
    elif choose == 3:
        '''Open interface'''
        interface.create()
    else:
        print(file.colours.RED + 'Invalid option' + file.colours.ENDC)
        sys.exit()


def autoplay():
    """
    Autoplay script that helps to choose the function desired
    :return: number int
    """
    print(file.colours.BLUE + "Biomek Script" + file.colours.ENDC)
    print('Please choose one option:\n')
    choose = input(file.colours.RED + '0' + file.colours.ENDC + ' -> Create a CSV file template\n'
                   + file.colours.RED + '1' + file.colours.ENDC + ' -> Create a Normalization CSV file\n'
                   + file.colours.RED + '2' + file.colours.ENDC + ' -> Create a CSV file with combinatorial\n'
                   +'Choose > ')

    return int(choose)
""" Miscellaneous useful functions.
    Methods for converting to and from plate coordinates.
    Some functions were inherited From Plateo> https://github.com/Edinburgh-Genome-Foundry/Plateo.git)
    Methods to calc normalization sample file
"""

import numpy as np
import re


def final_concentration_fmol(concentration):
    if concentration < 100:
        final_concent = 20
    else:
        final_concent = 40
    return final_concent


def fmol(length, concentration):
    """Return 20fmol or 40fmol of sample based on its length and concentration"""
    try:
        length = float(length)
        concentration = float(concentration)
    except TypeError:
        print(str(length) + 'is not a number')
    else:
        '''Choose 20fmol or 40fmol based on sample concentration'''
        concent_fmol = final_concentration_fmol(concentration)

        fmol = round((float(concent_fmol)/1000) * 660 * 1 / 10 ** 6 * length * 1000, 2)
        return fmol, concent_fmol


def dilution_factor(fmol, concentration):
    """Return the needed volume of sample considering its concentration"""
    try:
        concentration = float(concentration)
    except TypeError:
        print(str(concentration) + 'is not a number')
    else:
        dilut_factor = round(1/(fmol/concentration), 2)
        return dilut_factor


def sample_volume(dilut_factor, well_min_vol):
    return round(well_min_vol/dilut_factor, 2)


def total_volume(sample_volume, dilut_factor):
    total_volume = sample_volume * dilut_factor
    return total_volume


def total_destination_plates(plates_in, in_well, out_well):
    """Return the number of destination plates"""
    num_dest = len(plates_in) * in_well/out_well
    if num_dest < 1:
        num_dest = 1
    return num_dest


def water_volume(total_volume, sample_volume):
    """Return the volume of water to complete 50ul"""
    vol_water = round(total_volume - sample_volume, 2)
    return vol_water


def rows_columns(num_wells):
    """Convert 96->(8,12), 384->(16,24), etc."""
    # a = int(np.round(np.sqrt(num_wells / 6)))
    a = np.sqrt(num_wells / 6)
    n_rows = int(np.round(2*a))
    n_columns = int(np.round(3*a))
    return n_rows, n_columns


def rowname_to_number(name):
    "Convert A->1 Z->26 AA->27 etc."
    if len(name) == 2:
        return 26 * rowname_to_number(name[0]) + rowname_to_number(name[1])
    try:
        return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.index(name)
    except:
        raise ValueError(name + " is not a valid row name.")


def number_to_rowname(number):
    "Convert 0->A 25->Z 27->AA etc."
    if number > 26:
        return number_to_rowname(int(number / 26)) +\
               number_to_rowname(number % 26)
    return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[number]


def wellname_to_coordinates(wellname):
    """Convert A1->(1,1), H11->(8, 11), etc."""
    rowname, colname = re.match("([a-zA-Z]+)([0-9]+)", wellname).groups()
    return rowname_to_number(rowname), int(colname)-1


def coordinates_to_wellname(coords):
    """Convert (0,0)->A1, (4,3)->D5, (12, 12)->M13, etc."""
    row, column = coords
    return number_to_rowname(row)+str(column+1)
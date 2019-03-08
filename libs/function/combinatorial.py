from ..misc import file, calc
import itertools


def get_sets_in_filepath(reader):
    lists_parts = []
    lists_combination_parts = []
    ''' For each line in file get the list'''
    for line in reader:
        parts = []
        sets = line.strip('\n').split(';')
        '''List of parts'''
        for set in sets:
            parts.append(set.split(','))
        ''' Create the single list of parts'''
        lists_parts.append(list(parts))
        ''' Create the combinations from the list'''
        lists_combination_parts.append(list(itertools.product(*parts)))
    return lists_combination_parts, lists_parts


def run_combination(path, filename):
    filein = file.verify(path + "/" + filename)

    """Create combinations"""
    lists_combination_parts, lists_parts = get_sets_in_filepath(filein)

    """Calculate the num of parts in input file"""
    list_set_num_parts = calc.num_listsparts(lists_parts)

    """Calculate number of combinations"""
    num_combinations_in_list = calc.num_combinations(lists_combination_parts)

    """Write a output file"""
    fileout = file.create(path+"/"+'combination_' + str(filename), 'w')
    file.write_combinations(fileout, lists_combination_parts)
    fileout.close()

    return fileout, list_set_num_parts, num_combinations_in_list


from ..misc import file
import itertools


def get_sets_in_filepath(reader):
    lists_combination_parts = []
    ''' For each line in file get the list'''
    for line in reader:
        parts = []
        sets = line.strip('\n').split(';')
        '''List of parts'''
        for set in sets:
            parts.append(set.split(','))
        ''' Create the combinations from the list'''
        lists_combination_parts.append(list(itertools.product(*parts)))
    return lists_combination_parts


def run_combination(path, filename):
    filein = file.verify(path + "/" + filename)

    """Create combinations"""
    lists_combination_parts = get_sets_in_filepath(filein)

    """Write a output file"""
    fileout = file.create(path+"/"+'combination_' + str(filename), 'w')
    file.write_combinations(fileout, lists_combination_parts)
    fileout.close()

    return fileout


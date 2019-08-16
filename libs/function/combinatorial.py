import itertools, csv, os
from ..biofoundry import db
from ..misc import file, calc



def get_combinations(parts):
    ''' Create the single list of parts'''
    lists_parts = list(parts)
    ''' Create the combinations from the list'''
    lists_combination_parts = list(itertools.product(*parts))
    return lists_combination_parts, lists_parts


def get_sets(parts_dct, header):
    parts = []
    for i in range(1, len(header)):
        set = []
        for row in parts_dct:
            if row[header[i]] != '':
                set.append(row[header[i]])
        if len(set) > 0:
            parts.append(list(set))
    return parts


def run_combination(path, filename, user):
    lists_parts = []
    lists_combination_parts = []

    filein = file.verify(path + "/" + filename)
    with open(filein.name, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        header = reader.fieldnames
        exp_id = -1
        parts_dct = []

        for dct in map(dict, reader):
            if exp_id == -1: exp_id = dct[header[0]]
            if dct[header[0]] == exp_id:
                parts_dct.append(dct)
            else:
                exp_id = dct[header[0]]
                parts = get_sets(parts_dct, header)
                l_combination_parts, l_parts = get_combinations(parts)
                lists_combination_parts.append(list(l_combination_parts))
                lists_parts.append(list(l_parts))
                parts_dct = []
                parts_dct.append(dct)

        parts = get_sets(parts_dct, header)
        l_combination_parts, l_parts = get_combinations(parts)
        lists_combination_parts.append(list(l_combination_parts))
        lists_parts.append(list(l_parts))

    """Calculate the num of parts in input file"""
    list_set_num_parts = calc.num_listsparts(lists_parts)

    """Calculate number of combinations"""
    num_combinations_in_list = calc.num_combinations(lists_combination_parts)

    """Write a output file"""
    outfile_name = 'combination_' + str(filename)
    fileout = file.create(path+"/docs/"+outfile_name, 'w')
    file.write_combinations(fileout, lists_combination_parts)
    # outfile_name = os.path.basename(fileout)
    # print(outfile_name)
    db_outfile = db.save_file(outfile_name, 'Combinatorial', user)

    fileout.close()

    return db_outfile, list_set_num_parts, num_combinations_in_list

















        # for dct in map(dict, reader):
        #     exp_id = dct[header[0]]
        #     parts = []
        #
        #
        #
        #
        #     if firstline:
        #         firstline = False
        #         exp_id = dct[header[0]]
        #         for i in range(1, len(dct)):
        #             if dct[header[i]] != '':
        #                 parts.append(dct[header[i]])
        #         print(parts)
        #
        #     if exp_id == dct[header[0]]:
        #         print(dct[header[0]])
        #
        #     else:
        #         exp_id = dct[header[0]]
        #         print(dct[header[0]])




    # """Create combinations"""
    # lists_combination_parts, lists_parts = get_sets_in_filepath(filein)
    #
    # """Calculate the num of parts in input file"""
    # list_set_num_parts = calc.num_listsparts(lists_parts)
    #
    # """Calculate number of combinations"""
    # num_combinations_in_list = calc.num_combinations(lists_combination_parts)
    #
    # """Write a output file"""
    # fileout = file.create(path+"/"+'combination_' + str(filename), 'w')
    # file.write_combinations(fileout, lists_combination_parts)
    # fileout.close()
    #
    # return fileout, list_set_num_parts, num_combinations_in_list
    return None, None, None


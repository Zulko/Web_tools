import os
import dnacauldron as dc
from Bio import Restriction
import zipfile
from ..misc import file
from ..biofoundry import db


def has_less_than_2_bsmbi_sites(fragment):
    sites = Restriction.BsmBI.search(fragment.seq, linear=False)
    return len(sites) < 2


def has_less_than_2_bsai_sites(fragment):
    sites = Restriction.BsaI.search(fragment.seq, linear=False)
    return len(sites) < 2


def get_partname(path):
    files_name = os.listdir(path)
    return files_name


# def build_entry_vector(path, ENZYME):
#     files_name = get_partname(path)
#
#     for file_name in files_name:
#         file_name = file_name.replace(".gb", "")
#         if file_name != "pYTK001":
#             parts_names = ["pYTK001", file_name]
#             new_name = file_name.replace('type3', 'entry')
#
#             all_records_parts = [
#                 dc.load_record(os.path.join(path, part_name + '.gb'),
#                                id=part_name, linear=False)
#                 for part_name in parts_names
#             ]
#             if ENZYME == "BsmBI":
#                 mix = dc.RestrictionLigationMix(
#                     constructs=all_records_parts,
#                     enzyme="BsmBI",
#                     fragments_filters=(has_less_than_2_bsmbi_sites,)
#                 )
#             else:
#                 mix = dc.RestrictionLigationMix(
#                     constructs=all_records_parts,
#                     enzyme="BsaI",
#                     fragments_filters=(has_less_than_2_bsai_sites,)
#                 )
#
#             circular_assemblies = list(mix.compute_circular_assemblies())
#             print ("%d assemblies found for %s" % (len(circular_assemblies),str(file_name)))
#
#             if len(circular_assemblies) > 1:
#                 for i in range(0, len(circular_assemblies)):
#                     new_name = new_name.replace(".gb","")
#                     dc.write_record(circular_assemblies[i], new_name + str(i+1) +'.gb')
#             if len(circular_assemblies) == 1:
#                 dc.write_record(circular_assemblies[0], new_name + ".gb")
#
#
# def generate_TU_file(file_name, parts_names, ENZYME):
#     new_name = file_name.replace('entry', 'TU')
#
#     all_records_parts = [
#         dc.load_record(os.path.join(path, part_name + '.gb'),
#                        id=part_name, linear=False)
#         for part_name in parts_names
#     ]
#     if ENZYME == "BsmBI":
#         mix = dc.RestrictionLigationMix(
#             constructs=all_records_parts,
#             enzyme="BsmBI",
#             fragments_filters=(has_less_than_2_bsmbi_sites,)
#         )
#     else:
#         mix = dc.RestrictionLigationMix(
#             constructs=all_records_parts,
#             enzyme="BsaI",
#             fragments_filters=(has_less_than_2_bsai_sites,)
#         )
#
#     circular_assemblies = list(mix.compute_circular_assemblies())
#     print ("%d assemblies found for %s" % (len(circular_assemblies),str(file_name)))
#
#     if len(circular_assemblies) > 1:
#         for i in range(0, len(circular_assemblies)):
#             new_name = new_name.replace(".gb","")
#             dc.write_record(circular_assemblies[i], new_name + str(i+1) +'.gb')
#     if len(circular_assemblies) == 1:
#         dc.write_record(circular_assemblies[0], new_name + ".gb")
#
#
# def build_tu(path, ENZYME):
#     files_name = get_partname(path)
#     for file_name in files_name:
#         file_name = file_name.replace(".gb","")
#
#         if file_name.startswith("MSH_"):
#             parts_names = ["pYTK002", "pYTK009", "pYTK056", "pYTK067", "pYTK095", file_name]
#             generate_TU_file(file_name, parts_names, ENZYME)
#
#         elif file_name.startswith("P6H_"):
#             parts_names = ["pYTK003", "pYTK010", "pYTK055", "pYTK068", "pYTK095", file_name]
#             generate_TU_file(file_name, parts_names, ENZYME)
#
#         elif file_name.startswith("CPR_"):
#             parts_names = ["pYTK004", "pYTK018", "pYTK053", "pYTK072", "pYTK095", file_name]
#             generate_TU_file(file_name, parts_names, ENZYME)
#
#
# def build_multi_tu(path, filein_name, ENZYME):
#     filein = open(os.path.join(path, filein_name), 'r')
#     for row in filein:
#         file_name = ''
#         parts_names = row.strip().split(",")
#         for part in parts_names:
#             if part != 'pYTK096':
#                 file_name += part.replace('_TU', '')
#                 file_name += '-'
#         file_name += 'URA'
#
#         all_records_parts = [
#             dc.load_record(os.path.join(path, part_name + '.gb'),
#                            id=part_name, linear=False)
#             for part_name in parts_names
#         ]
#         if ENZYME == "BsmBI":
#             mix = dc.RestrictionLigationMix(
#                 constructs=all_records_parts,
#                 enzyme="BsmBI",
#                 fragments_filters=(has_less_than_2_bsmbi_sites,)
#             )
#         else:
#             mix = dc.RestrictionLigationMix(
#                 constructs=all_records_parts,
#                 enzyme="BsaI",
#                 fragments_filters=(has_less_than_2_bsai_sites,)
#             )
#
#         circular_assemblies = list(mix.compute_circular_assemblies())
#         print("%d assemblies found for %s" % (len(circular_assemblies), str(file_name)))
#
#         if len(circular_assemblies) > 1:
#             for i in range(0, len(circular_assemblies)):
#                 new_name = file_name.replace(".gb", "")
#                 dc.write_record(circular_assemblies[i], new_name + str(i + 1) + '.gb')
#         if len(circular_assemblies) == 1:
#             dc.write_record(circular_assemblies[0], file_name + ".gb")


def build_plasmid(filein, out_zip, path, topology, ENZYME):
    i = 0
    dest_dir = path.replace(os.path.dirname(path), '', 1)
    for line in filein:
        i+=1
        file_name = 'assembly'
        parts_names = list(line.strip("\n").split(','))

        all_records_parts = [
            dc.load_record(os.path.join(path, part_name + ".gb"),
                           id=part_name, topology=topology)
            for part_name in parts_names
        ]

        if ENZYME == "BsmBI":
            mix = dc.RestrictionLigationMix(
                constructs=all_records_parts,
                enzyme="BsmBI",
                fragments_filters=(has_less_than_2_bsmbi_sites,)
            )
        else:
            mix = dc.RestrictionLigationMix(
                constructs=all_records_parts,
                enzyme="BsaI",
                fragments_filters=(has_less_than_2_bsai_sites,)
            )

        circular_assemblies = list(mix.compute_circular_assemblies())
        # print("%d assemblies found for %s" % (len(circular_assemblies), str(file_name)))

        if len(circular_assemblies) > 1:
            for i in range(0, len(circular_assemblies)):
                file_name = file_name.replace(".gb", "")
                dc.write_record(circular_assemblies[i], path + '/' + file_name + str(i+1) + ".gb")
                out_zip.write(os.path.join(path, file_name + str(i+1) + ".gb"), arcname=os.path.join(dest_dir, file_name + str(i+1) + ".gb"))
                out_zip.write(path + '/' + file_name + str(i+1) + ".gb")
        if len(circular_assemblies) == 1:
            dc.write_record(circular_assemblies[0], path + '/' + file_name + ".gb")
            out_zip.write(os.path.join(path, file_name + ".gb"), arcname=os.path.join(dest_dir, file_name + ".gb"))
    return out_zip


def search_in_zip(part, zip):
    for genbank in zip.namelist():
        genbankname = genbank.strip(".gb")
        if genbankname == part:
            return True
    return False


def check_files_match(filein, zip):
    alert = []
    for line in filein:
        parts = line.strip("\n").split(',')
        for part in parts:
            found = search_in_zip(part, zip)
            if found == False:
                alert.append('Missing file or misspelling genbank filename in zipfile for: %s.' % part)
                print('Missing file or misspelling genbank filename in zipfile for: %s.' % part)
    filein.seek(0)
    return alert


def run(path, combination_filename, zip_filename, topology, enzyme, user):
    alerts = []
    filein = file.verify(path + "/" + combination_filename)
    zip = zipfile.ZipFile(path + "/" + zip_filename)
    temp_folder = path + "/contructor/"

    alert = check_files_match(filein, zip)
    if len(alert) > 0:
        alerts.append(alert)
        return alerts, None
    else:
        '''create an output zipfile'''
        out_zip = zipfile.ZipFile(path + "/docs/" + "assemblies.zip", "w")

        '''extract zip file'''
        with zipfile.ZipFile(path + "/" + zip_filename) as zf:
            zf.extractall(temp_folder)
        filled_out_zip = build_plasmid(filein, out_zip, temp_folder, topology, enzyme)

        zip_out = db.save_file('assemblies.zip', 'Cauldron', user)

    return alerts, zip_out

    # '''Delete temp files'''
    # for zip_filename in temp_folder:
    #     os.unlink(zip_filename)
    # os.mkdir(temp_folder)




# if __name__ == '__main__':
#     path = '/home/flavia/PycharmProjects/DnaCauldron/tests/data/assemblies/build_EV'
#     build_entry_vector(path, ENZYME="BsmBI")
    # path = '/home/flavia/PycharmProjects/DnaCauldron/tests/data/assemblies/build_TU'
    # build_tu(path, ENZYME="BsaI")
    # path = '/home/flavia/PycharmProjects/DnaCauldron/tests/data/assemblies/build_multi_TU'
    # file_name = 'sanguinarine_combinatorial.txt'
    # build_multi_tu(path, file_name, ENZYME="BsmBI")
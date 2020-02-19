from ..misc import file as f
from ..biofoundry import db

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC
from Bio.SeqFeature import SeqFeature, FeatureLocation
from zipfile import ZipFile

import os


def generate_from_csv(path, filename, user):
    filein = f.verify(path + "/" + filename)
    csv_file = f.create_reader_csv(filein)
    header = next(csv_file)
    list_to_zip = []
    db_gbfiles = 'result_' + os.path.splitext(filename)[0] + '.zip'

    for row in csv_file:
        name = row[0]
        description = row[1]
        sequence = row[2]
        list_to_zip.append(generate_from_sequence(sequence, name, description, path))

        ''' Create a zip file and return it'''
        with ZipFile(path + '/docs/' + db_gbfiles, 'w') as zip:
            for file in list_to_zip:
                zip.write(file, os.path.basename(file))

    db_zip = db.save_file(db_gbfiles, 'Genbank', user)
    return db_zip


def generate_from_sequence(sequence, name, description, path):
    # Create a sequence
    sequence_string = sequence
    sequence_object = Seq(sequence_string, IUPAC.unambiguous_dna)

    # Create a record
    record = SeqRecord(sequence_object,
                       id='123456789',  # random accession number
                       name=name,
                       description=description)

    # Add annotation
    # feature = SeqFeature(FeatureLocation(start=3, end=12), type='misc_feature')
    # record.features.append(feature)

    # Save as GenBank file
    file_path = path + "/docs/" + str(name) + ".gb"
    output_file = open(file_path, 'w')
    SeqIO.write(record, output_file, 'genbank')

    return file_path

#! usr/bin/python2.7
##
##
# Concordia Genome Foundry
# author: Flavia Araujo - Adapted from Jon Laurent
# date: February 4th, 2019
# sudo apt install primer3


import os, glob
import subprocess
from Bio import SeqIO


def load_seqs(path, fastafile):
    seqlist = list(SeqIO.parse(open(path + '/' + fastafile,"rU"),"fasta"))
    #fastafile.close()

    na_seqs = [record for record in seqlist if len(record.seq) < 50 or "N" in record.seq[0:50] or "N" in record.seq[(len(record.seq)-50):len(record.seq)] ]
    nafile = open(path + '/' + fastafile+"-invalidseqs.fasta","w")
    SeqIO.write(na_seqs, nafile, "fasta")
    nafile.close()

    valid_seqs = [record for record in seqlist if len(record.seq) > 50 and "N" not in record.seq[0:50] and "N" not in record.seq[(len(record.seq)-50):len(record.seq)] ]
    validfile = open(path + '/' + fastafile+"-validseqs.fasta","w")
    SeqIO.write(valid_seqs, validfile, "fasta")
    validfile.close()
    return valid_seqs


def make_boulderio(seqid, seq, start, end):
    if end.find('length') == -1:
        length = int(end)
    else:
        length = len(seq) - 1
    boulder = {
    "SEQUENCE_ID":seqid,
    "SEQUENCE_TEMPLATE":seq,
    "SEQUENCE_FORCE_LEFT_START":start,
    "SEQUENCE_FORCE_RIGHT_START":length,
    # "SEQUENCE_FORCE_LEFT_START": 0,
    # "SEQUENCE_FORCE_RIGHT_START": length,
    "PRIMER_TASK":"generic",
    "PRIMER_PICK_LEFT_PRIMER":5,
    "PRIMER_PICK_INTERNAL_OLIGO":0,
    "PRIMER_PICK_RIGHT_PRIMER":5,
    "PRIMER_PRODUCT_SIZE_RANGE":"50-"+str(len(seq)),
    "PRIMER_OPT_SIZE":15,
    "PRIMER_MIN_SIZE":15,
    "PRIMER_MAX_SIZE":35,
    "PRIMER_MAX_POLY_X":10,
    "PRIMER_MIN_TM":50,
    "PRIMER_OPT_TM":60,
    "PRIMER_MAX_TM":72,
    "PRIMER_PAIR_MAX_DIFF_TM":8,
    "PRIMER_MIN_GC":20.0,
    "PRIMER_MAX_HAIRPIN_TH":100.0,
    "P3_FILE_FLAG":1,
    "PRIMER_EXPLAIN_FLAG":1,
    }

    boulderfile = seqid+".boulderio"
    with open(boulderfile,"w") as boulderf:
        for param in boulder.keys():
            boulderf.write(str(param+"="+str(boulder[param])+"\n"))
        boulderf.write("="+"\n")
    return str(boulderfile)


def run_primer3(boulderfile):
    primer3out = subprocess.check_output(["primer3_core", boulderfile]).decode("ascii")
    return primer3out


def make_primerout_dict(primer3out):
    primeroutdict = {}
    primerinfolist=primer3out.strip().split("\n")
    for line in primerinfolist:
        #if line.strip() == "=": next
        entry = line.strip().split("=")
        primeroutdict[entry[0]] = entry[1]
    return primeroutdict


def create_output_file(path, fastafile):
    outfile = open(path + '/' + fastafile + ".primers", "w")
    outfile.write(
        "GeneID" + "\t" + "UpstreamPrimerSequence" + "\t" + "DownstreamPrimerSequence" + "\t" + "UpstreamPrimerLength" + "\t" + "DownstreamPrimerLength" + "\t" + "ProductLength" + "\t" + "UpstreamPrimerTm" + "\t" + "DownstreamPrimerTm" + "\n")
    return outfile


def run_primer(path, fastafile, start, end):
    '''Read the fasta sequences from input file'''
    seqs = load_seqs(path, fastafile)
    stubbornseqs = []
    '''Create a output file for the primers'''
    outfile = create_output_file(path, fastafile)

    for record in seqs:
        boulderfile = make_boulderio(record.id, str(record.seq), int(start), end)
        primer3out = run_primer3(boulderfile)
        primerdict = make_primerout_dict(primer3out)
        if "PRIMER_LEFT_0_SEQUENCE" not in primerdict.keys() or "PRIMER_RIGHT_0_SEQUENCE" not in primerdict.keys():
            stubbornseqs.append(record)
        else:
            outfile.write(record.id + "\t" + primerdict["PRIMER_LEFT_0_SEQUENCE"] + "\t" + primerdict[
                "PRIMER_RIGHT_0_SEQUENCE"] + "\t" + str(len(primerdict["PRIMER_LEFT_0_SEQUENCE"])) + "\t" + str(
                len(primerdict["PRIMER_RIGHT_0_SEQUENCE"])) + "\t" + primerdict[
                              "PRIMER_PAIR_0_PRODUCT_SIZE"] + "\t" + primerdict["PRIMER_LEFT_0_TM"] + "\t" +
                          primerdict["PRIMER_RIGHT_0_TM"] + "\n")
        #   print seqs[record].id+"\t"+primerdict["PRIMER_LEFT_0_SEQUENCE"]+"\t"+str(len(primerdict["PRIMER_LEFT_0_SEQUENCE"]))+"\t"+primerdict["PRIMER_LEFT_0_TM"]
        subprocess.call(["rm", boulderfile])
        subprocess.call(["rm", record.id + ".for"])
        subprocess.call(["rm", record.id + ".rev"])

    # with open(fastafile + "-stubbornseqs.fasta", "w") as stubbornfile:
    #     SeqIO.write(stubbornseqs, stubbornfile, "fasta")

    outfile.close()
    return outfile

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
from ..biofoundry import db


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


def check_primers_pos(start, end, seq, seqid):
    length = len(seq)
    rev_start = length - int(end) -1

    if start >= len(seq):
        alert = 'Forward primer for sequence ' + seqid + ' start position exceeds sequence length.'
        return alert
    elif rev_start <= 0:
        alert = 'Reverse primer for sequence ' + seqid + ' start position exceeds sequence length.'
        return alert
    else:
        return None


def make_boulderio(seqid, seq, start, end, size_min_prime, size_opt_prime, size_max_prime,
                   tm_min_prime, tm_opt_prime, tm_max_prime, tm_max_pair_prime, tm_gc_perc):

    length = len(seq)
    if end != 0:
        length = length - int(end) -1
    else:
        length -= 1

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
    "PRIMER_OPT_SIZE":size_opt_prime,
    "PRIMER_MIN_SIZE":size_min_prime,
    "PRIMER_MAX_SIZE":size_max_prime,
    "PRIMER_MAX_POLY_X":10,
    "PRIMER_MIN_TM":tm_min_prime,
    "PRIMER_OPT_TM":tm_opt_prime,
    "PRIMER_MAX_TM":tm_max_prime,
    "PRIMER_PAIR_MAX_DIFF_TM":tm_max_pair_prime,
    "PRIMER_MIN_GC":tm_gc_perc,
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
    outfile = open(path + '/docs/' + fastafile + ".primers", "w")
    outfilename = fastafile + ".primers"
    outfile.write(
        "GeneID" + "\t" + "UpstreamPrimerSequence" + "\t" + "DownstreamPrimerSequence" + "\t" + "UpstreamPrimerLength" + "\t" + "DownstreamPrimerLength" + "\t" + "ProductLength" + "\t" + "UpstreamPrimerTm" + "\t" + "DownstreamPrimerTm" + "\n")
    return outfile, outfilename


def run_primer(path, fastafile, start, end, size_min_prime,
                                        size_opt_prime, size_max_prime, tm_min_prime, tm_opt_prime, tm_max_prime, tm_max_pair_prime, tm_gc_perc, user):
    '''Read the fasta sequences from input file'''
    seqs = load_seqs(path, fastafile)
    alert = []
    if len(seqs) < 1:
        alert = 'Please, check the input file format'
        return None, alert

    stubbornseqs = []
    '''Create a output file for the primers'''
    outfile, outfilename = create_output_file(path, fastafile)

    for record in seqs:
        alert = check_primers_pos(int(start), int(end), str(record.seq), record.id)

        if alert is None:
            boulderfile = make_boulderio(record.id, str(record.seq), int(start), int(end), int(size_min_prime),
                                         int(size_opt_prime), int(size_max_prime), int(tm_min_prime),
                                         int(tm_opt_prime), int(tm_max_prime), int(tm_max_pair_prime), int(tm_gc_perc))
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
        else:
            return None, alert

    output_file = db.save_file(outfilename, 'Script: Primer3', user)
    outfile.close()
    return output_file, alert

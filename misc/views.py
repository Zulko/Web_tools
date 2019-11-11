from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render

from libs.misc.genbank import generate_from_csv
from libs.misc.nrc_sequence import run_nrc_sequence
from libs.function.fasta2primer3 import run_primer
from libs.function.normalization import run_normalization

import os


def upload_file(request, filename):
    upload = request.FILES[filename]
    fs = FileSystemStorage()
    name = fs.save(upload.name, upload)
    url = fs.url(name)
    return upload, fs, name, url


def genbank(request):
    if request.method == "POST":
        user = request.user
        if len(request.FILES) != 0:
            upload, fs, name, url = upload_file(request, 'myFile')

            ''' Calling Python Script'''
            outfile = generate_from_csv(settings.MEDIA_ROOT, name, user)
            if outfile is not None:
                outfile_name = str(outfile)
                outfile_url = fs.url(outfile_name)
                return render(request, 'misc/genbank.html',
                              {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name,
                               'outfile_url': outfile_url})

    return render(request, 'misc/genbank.html',
                  {'uploadfile_name': '', 'url': '', 'outfile_name': '', 'outfile_url': ''})


def primer(request):
    if request.method == 'POST':
        user = request.user
        if len(request.FILES) != 0:
            upload, fs, name, url = upload_file(request, 'myFile')
            start_prime = request.POST['start_prime']
            end_prime = request.POST['end_prime']

            ''' Calling Python Script'''
            outfile, alert = run_primer(settings.MEDIA_ROOT, name, start_prime, end_prime, user)
            if outfile is not None:
                outfile_name = os.path.basename(outfile.name)
                outfile_url = fs.url(outfile_name)
                return render(request, 'misc/primer.html', {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name, 'outfile_url': outfile_url})
            else:
                return render(request, 'misc/primer.html',
                              {'uploadfile_name': upload.name, 'url': url, 'outfile_name': '',
                               'outfile_url': '', 'alert': alert})
        else:
            alert = 'Input file not found'
            return render(request, 'misc/primer.html', {'uploadfile_name': '', 'url': '', 'outfile_name': '', 'abs_path': '', 'alert': alert})
    return render(request, 'misc/primer.html', {'uploadfile_name': '', 'url': '', 'outfile_name': '', 'abs_path': ''})


def normalization(request):
    if request.method == "POST":
        user = request.user
        if len(request.FILES) != 0:
            upload, fs, name, url = upload_file(request, 'upload_file')
            in_well = request.POST['num_well_source']
            out_well = request.POST['num_well_destination']
            bb_fmol = request.POST['bb_fmol']
            part_fmol = request.POST['part_fmol']

            ''' Calling Python Script'''
            outfile, alert = run_normalization(settings.MEDIA_ROOT, name, int(in_well), int(out_well), int(bb_fmol), int(part_fmol), user)
            if outfile is not None:
                outfile_name = str(outfile)
                print(outfile_name)
                outfile_url = fs.url(outfile_name)
                return render(request, 'misc/normalization.html', {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name, 'outfile_url': outfile_url, 'alert':alert})
            else:
                return render(request, 'misc/normalization.html',
                              {'uploadfile_name': upload.name, 'url': url, 'outfile_name': '',
                               'outfile_url': '', 'alert': alert})
    return render(request, 'misc/normalization.html', {'uploadfile_name': '', 'url': '', 'outfile_name': '', 'outfile_url': '', 'alert': ''})


def nrc_sequence(request):
    if request.method == "POST":
        user = request.user
        if len(request.FILES) != 0:
            upload, fs, name, url = upload_file(request, 'upload_file')
            sequence = request.POST['sequence']

            ''' Calling Python Script'''
            outfile, alert = run_nrc_sequence(settings.MEDIA_ROOT, name, sequence, user)
            if outfile is not None:
                outfile_name = str(outfile)
                outfile_url = fs.url(outfile_name)
                return render(request, 'misc/nrc_sequence.html', {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name, 'outfile_url': outfile_url, 'alert':alert})
            else:
                return render(request, 'misc/nrc_sequence.html',
                              {'uploadfile_name': upload.name, 'url': url, 'outfile_name': '',
                               'outfile_url': '', 'alert': alert})
    return render(request, 'misc/nrc_sequence.html', {'uploadfile_name': '', 'url': '', 'outfile_name': '', 'outfile_url': '', 'alert': ''})
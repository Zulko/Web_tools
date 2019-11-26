from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from libs.misc.genbank import generate_from_csv
from libs.misc.nrc_sequence import run_nrc_sequence
from libs.misc.echo_transfer import run_echo_transfer_from_worklist
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
            size_min_prime = request.POST['size_min_prime']
            size_opt_prime = request.POST['size_opt_prime']
            size_max_prime = request.POST['size_max_prime']
            tm_min_prime = request.POST['tm_min_prime']
            tm_opt_prime = request.POST['tm_opt_prime']
            tm_max_prime = request.POST['tm_max_prime']
            tm_max_pair_prime = request.POST['tm_max_pair_prime']
            tm_gc_perc = request.POST['tm_gc_perc']

            ''' Calling Python Script'''
            outfile, alert = run_primer(settings.MEDIA_ROOT, name, start_prime, end_prime, size_min_prime,
                                        size_opt_prime, size_max_prime, tm_min_prime, tm_opt_prime, tm_max_prime,
                                        tm_max_pair_prime, tm_gc_perc, user)
            if outfile is not None:
                return render(request, 'misc/primer.html', {'uploadfile_name': upload.name, 'url': url, 'outfile': outfile})
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


@login_required(login_url="/accounts/login/")
def echo_transfer_db(request):
    if request.method == "POST":
        scriptname = 'Echo Transfer from Worklist'
        user = request.user
        if len(request.FILES) != 0:
            upload, fs, name_file, url_file = upload_file(request, 'upload_file')

            """Dispenser parameters"""
            machine = request.POST['machine']
            min_vol = request.POST['min_vol']
            vol_resol = request.POST['vol_resol']
            dead_vol = request.POST['dead_vol']
            dispenser_parameters = machine, float(min_vol) * 1e-3, float(vol_resol) * 1e-3, float(dead_vol)

            """Reaction parameters"""
            template_conc = request.POST['template_conc']
            primer_f = request.POST['primer_f']
            primer_r = request.POST['primer_r']
            # per_phusion = request.POST['phusion']
            # per_buffer = request.POST['buffer']
            # per_dntps = request.POST['dntps']
            # total_vol = request.POST['total_vol']
            # mantis_two_chips = 'mantis_two_chips' in request.POST
            # add_water = 'add_water' in request.POST
            mix_parameters = \
                float(template_conc), \
                float(primer_f), \
                float(primer_r), \
                # float(per_buffer), \
                # float(per_phusion), \
                # float(per_dntps), \
                # float(total_vol), \
                # add_water

            """Destination plate"""
            num_well_destination = request.POST['num_well_destination']
            pattern = request.POST['pattern']

            ''' Calling Python Script'''
            alerts, outfile_robot = run_echo_transfer_from_worklist(settings.MEDIA_ROOT,
                  name_file, dispenser_parameters, mix_parameters, int(num_well_destination), int(pattern), user, scriptname)

            if len(alerts) == 0:
                return render(request, 'misc/echo_transfer.html', {'uploadfile_name': upload, 'url_file': url_file,
                                                      'outfile_robot': outfile_robot, 'alerts': alerts})
            else:
                return render(request, 'misc/echo_transfer.html',
                              {'uploadfile_name': upload, 'url_file': url_file,
                               'outfile_mantis': '', 'outfile_robot': '',
                               'alerts': alerts, 'mixer_recipe': '', 'chip_mantis': ''})
    return render(request, 'misc/echo_transfer.html')
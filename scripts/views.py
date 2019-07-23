from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required

from libs.function.spotting import run_spotting
from libs.function.combinatorial import run_combination
from libs.function.moclo import run_moclo
from libs.function.moclo_db import run_moclo_db

import os


def upload_file(request, filename):
    upload = request.FILES[filename]
    fs = FileSystemStorage()
    name = fs.save(upload.name, upload)
    url = fs.url(name)
    return upload, fs, name, url


def spotting(request):
    context = {}
    if request.method == "POST":
        user = request.user
        num_sources = request.POST['num_sources']
        num_well = request.POST['num_well']
        num_pattern = request.POST['num_pattern']
        pattern = request.POST['pattern']
        ''' Calling Python Script'''
        outfile, worklist, alert = run_spotting(int(num_sources), int(num_well), int(num_pattern), int(pattern), user)

        if alert is not None:
            return render(request, 'scripts/spotting.html',
                          {'outfile_name': '', 'outfile_url': '',
                           'worklist_name': '', 'outfileworklist_url': '', 'alert': alert})
        else:
            return render(request, 'scripts/spotting.html', {'outfile': outfile, 'worklist': worklist})
    return render(request, 'scripts/spotting.html', {'outfile': '', 'worklist': ''})


# @login_required(login_url="/accounts/login/")
def combinatorial(request):
    if request.method == "POST":
        if len(request.FILES) != 0:
            upload, fs, name, url = upload_file(request, 'myFile')

            ''' Calling Python Script'''
            outfile, list_num_parts, list_num_combinations = run_combination(settings.MEDIA_ROOT, name)
            if outfile is not None:
                outfile_name = os.path.basename(outfile.name)
                outfile_url = fs.url(outfile_name)
                return render(request, 'scripts/combinatorial.html',
                              {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name,
                               'outfile_url': outfile_url, 'num_parts': list_num_parts, 'num_combin': list_num_combinations})
            else:
                return render(request, 'scripts/combinatorial.html',
                              {'uploadfile_name': '', 'url': '', 'outfile_name': '',
                               'outfile_url': '', 'num_parts': '', 'num_combin': ''})

    return render(request, 'scripts/combinatorial.html',
                  {'uploadfile_name': '', 'url': '', 'outfile_name': '',
                   'outfile_url': '', 'num_parts': '', 'num_combin': ''})


# @login_required(login_url="/accounts/login/")
def assembly(request):
    # if len(request.FILES) != 0:
    #     upload, fs, name, url = upload_file(request, 'myFile')
    return render(request, 'scripts/assembly.html',
                  {'uploadfile_name': '', 'url': '', 'outfile_name': '', 'outfile_url': '', 'num_parts': '', 'num_combin': ''})


# @login_required(login_url="/accounts/login/")
def moclo(request):
    if request.method == "POST":
        if len(request.FILES) != 0:
            upload_f, fs, name_file, url_file = upload_file(request, 'upload_file')
            upload_db, fs, name_db, url_db = upload_file(request, 'upload_db')

            """Dispenser parameters"""
            machine = request.POST['machine']
            min_vol = request.POST['min_vol']
            vol_resol = request.POST['vol_resol']
            dead_vol = request.POST['dead_vol']
            dispenser_parameters = machine, float(min_vol) * 1e-3, float(vol_resol) * 1e-3, float(dead_vol)

            """Mixer parameters"""
            part_fmol = request.POST['part_fmol']
            bb_fmol = request.POST['bb_fmol']
            total_vol = request.POST['total_vol']
            per_buffer = request.POST['buffer']
            per_enz_restric = request.POST['enz_restric']
            per_enz_ligase = request.POST['enz_ligase']
            mantis_two_chips = 'mantis_two_chips' in request.POST
            add_water = 'add_water' in request.POST
            mix_parameters = float(part_fmol), float(bb_fmol), float(total_vol), float(per_buffer), float(per_enz_restric), float(per_enz_ligase), add_water

            """Destination plate"""
            num_well_destination = request.POST['num_well_destination']
            pattern = request.POST['pattern']

            ''' Calling Python Script'''
            alerts, outfile_mantis, outfile_robot, mixer_recipe, chip_mantis = run_moclo(settings.MEDIA_ROOT, name_file, name_db, dispenser_parameters, mix_parameters, int(num_well_destination), int(pattern), mantis_two_chips)

            if mixer_recipe is not None:
                outfile_mantis_name = os.path.basename(outfile_mantis.name)
                outfile_robot_name = os.path.basename(outfile_robot.name)
                outfile_mantis_url = fs.url(outfile_mantis_name)
                outfile_robot_url = fs.url(outfile_robot_name)
                return render(request, 'scripts/moclo.html', {'uploadfile_name': upload_f, 'upload_db': upload_db, 'url_file': url_file, 'url_db': url_db,
                                                      'outfile_mantis_name': outfile_mantis_name, 'outfile_robot_name': outfile_robot_name,
                                                      'outfile_mantis_url': outfile_mantis_url, 'outfile_robot_url': outfile_robot_url, 'alerts': alerts, 'mixer_recipe': mixer_recipe, 'chip_mantis': chip_mantis})
            else:
                return render(request, 'scripts/moclo.html',
                              {'uploadfile_name': upload_f, 'upload_db': upload_db, 'url_file': url_file,
                               'url_db': url_db, 'outfile_mantis_name': '', 'outfile_robot_name': '',
                               'outfile_mantis_url': '', 'outfile_robot_url': '',
                               'alerts': alerts, 'mixer_recipe': '', 'chip_mantis': ''})
    return render(request, 'scripts/moclo.html')


@login_required(login_url="/accounts/login/")
def moclo_db(request):
    if request.method == "POST":
        if len(request.FILES) != 0:
            upload, fs, name_file, url_file = upload_file(request, 'upload_file')

            """Dispenser parameters"""
            machine = request.POST['machine']
            min_vol = request.POST['min_vol']
            vol_resol = request.POST['vol_resol']
            dead_vol = request.POST['dead_vol']
            dispenser_parameters = machine, float(min_vol) * 1e-3, float(vol_resol) * 1e-3, float(dead_vol)

            """Mixer parameters"""
            part_fmol = request.POST['part_fmol']
            bb_fmol = request.POST['bb_fmol']
            total_vol = request.POST['total_vol']
            per_buffer = request.POST['buffer']
            per_enz_restric = request.POST['enz_restric']
            per_enz_ligase = request.POST['enz_ligase']
            mantis_two_chips = 'mantis_two_chips' in request.POST
            add_water = 'add_water' in request.POST
            mix_parameters = float(part_fmol), float(bb_fmol), float(total_vol), float(per_buffer), float(per_enz_restric), float(per_enz_ligase), add_water

            """Destination plate"""
            num_well_destination = request.POST['num_well_destination']
            pattern = request.POST['pattern']

            ''' Calling Python Script'''
            alerts, outfile_mantis, outfile_robot, mixer_recipe, chip_mantis = run_moclo_db(settings.MEDIA_ROOT, name_file, dispenser_parameters, mix_parameters, int(num_well_destination), int(pattern), mantis_two_chips)

            if mixer_recipe is not None:
                outfile_mantis_name = os.path.basename(outfile_mantis.name)
                outfile_robot_name = os.path.basename(outfile_robot.name)
                outfile_mantis_url = fs.url(outfile_mantis_name)
                outfile_robot_url = fs.url(outfile_robot_name)
                return render(request, 'scripts/moclo_db.html', {'uploadfile_name': upload, 'url_file': url_file,
                                                      'outfile_mantis_name': outfile_mantis_name, 'outfile_robot_name': outfile_robot_name,
                                                      'outfile_mantis_url': outfile_mantis_url, 'outfile_robot_url': outfile_robot_url, 'alerts': alerts, 'mixer_recipe': mixer_recipe, 'chip_mantis': chip_mantis})
            else:
                return render(request, 'scripts/moclo_db.html',
                              {'uploadfile_name': upload, 'url_file': url_file,
                               'outfile_mantis_name': '', 'outfile_robot_name': '',
                               'outfile_mantis_url': '', 'outfile_robot_url': '',
                               'alerts': alerts, 'mixer_recipe': '', 'chip_mantis': ''})
    return render(request, 'scripts/moclo_db.html')





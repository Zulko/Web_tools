from django.http import HttpResponse
from django.shortcuts import render
from libs.function.spotting import run_spotting
from libs.function.normalization import run_normalization
from libs.function.fasta2primer3 import run_primer
from libs.function.combinatorial import run_combination
from libs.function.moclo2 import run_moclo
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
import os


# TODO: Automatically remove files from media
# @login_required(login_url="/accounts/login/")
def home(request):
    return render(request, 'home.html')


# @login_required(login_url="/accounts/login/")
def spotting(request):
    context = {}
    if request.method == "POST":
        num_sources = request.POST['num_sources']
        num_well = request.POST['num_well']
        num_pattern = request.POST['num_pattern']
        pattern = request.POST['pattern']
        ''' Calling Python Script'''
        outfile_name, worklist_name = run_spotting(int(num_sources), int(num_well), int(num_pattern), int(pattern))

        if worklist_name is not None:
            fs = FileSystemStorage()
            outfile_url = fs.url(os.path.basename(outfile_name))
            context['worklist_name'] = worklist_name
            outfileworklist_url = fs.url(os.path.basename(worklist_name))
            print(outfile_url, outfileworklist_url)
            return render(request, 'spotting.html', {'outfile_name': outfile_name, 'outfile_url': outfile_url, 'worklist_name': worklist_name, 'outfileworklist_url': outfileworklist_url})

        elif outfile_name is not None:
            fs = FileSystemStorage()
            context['outfile_name'] = outfile_name
            outfile_url = fs.url(os.path.basename(outfile_name))
            return render(request, 'spotting.html', {'outfile_name': outfile_name, 'outfile_url': outfile_url, 'worklist_name': '', 'outfileworklist_url': ''})
        else:
            return render(request, 'spotting.html', {'outfile_name': 'Choose a different parameters combination', 'outfile_url': '','worklist_name': '', 'outfileworklist_url': ''})
    return render(request, 'spotting.html', {'outfile_name': '', 'outfile_url': '', 'worklist_name': '', 'outfileworklist_url':''})


# @login_required(login_url="/accounts/login/")
def normalization(request):
    context = {}
    if request.method == "POST":
        if len(request.FILES) != 0:
            upload = request.FILES['myFile']
            fs = FileSystemStorage()
            name = fs.save(upload.name, upload)
            context['url'] = fs.url(name)
            url = fs.url(name)
            in_well = request.POST['num_well_source']
            out_well = request.POST['num_well_destination']
            bb_fmol = request.POST['bb_fmol']
            part_fmol = request.POST['part_fmol']
            ''' Calling Python Script'''
            outfile, alert = run_normalization(settings.MEDIA_ROOT, name, int(in_well), int(out_well), int(bb_fmol), int(part_fmol))
            if outfile is not None:
                outfile_name = os.path.basename(outfile.name)
                outfile_url = fs.url(outfile_name)
                return render(request, 'normalization.html', {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name,'outfile_url': outfile_url, 'alert':alert})
            else:
                return render(request, 'normalization.html',
                              {'uploadfile_name': upload.name, 'url': url, 'outfile_name': '',
                               'outfile_url': '', 'alert': alert})
    return render(request, 'normalization.html', {'uploadfile_name': '', 'url': '', 'outfile_name': '','outfile_url': '', 'alert':''})


# @login_required(login_url="/accounts/login/")
def primer(request):
    context = {}
    if request.method == 'POST':
        if len(request.FILES) != 0:
            upload = request.FILES['myFile']
            start_prime = request.POST['start_prime']
            end_prime = request.POST['end_prime']
            fs = FileSystemStorage()
            name = fs.save(upload.name, upload)
            context['url'] = fs.url(name)
            url = fs.url(name)
            ''' Calling Python Script'''
            outfile = run_primer(settings.MEDIA_ROOT, name, start_prime, end_prime)
            if outfile is not None:
                outfile_name = os.path.basename(outfile.name)
                outfile_url = fs.url(outfile_name)
                return render(request, 'primer.html', {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name,'outfile_url': outfile_url})
        else:
            return render(request, 'primer.html', {'uploadfile_name': '', 'url': '', 'outfile_name': 'Missing an Input File', 'abs_path': ''})
    return render(request, 'primer.html', {'uploadfile_name': '', 'url': '', 'outfile_name': '','abs_path': ''})


# @login_required(login_url="/accounts/login/")
def combinatorial(request):
    context = {}
    if request.method == "POST":
        if len(request.FILES) != 0:
            upload = request.FILES['myFile']
            fs = FileSystemStorage()
            name = fs.save(upload.name, upload)
            context['url'] = fs.url(name)
            url = fs.url(name)
            ''' Calling Python Script'''
            outfile, list_num_parts, list_num_combinations = run_combination(settings.MEDIA_ROOT, name)
            if outfile is not None:
                outfile_name = os.path.basename(outfile.name)
                outfile_url = fs.url(outfile_name)
                return render(request, 'combinatorial.html',
                              {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name,
                               'outfile_url': outfile_url, 'num_parts': list_num_parts, 'num_combin': list_num_combinations})
            else:
                return render(request, 'combinatorial.html',
                              {'uploadfile_name': '', 'url': '', 'outfile_name': '',
                               'outfile_url': '', 'num_parts': '', 'num_combin': ''})

    return render(request, 'combinatorial.html',
                  {'uploadfile_name': '', 'url': '', 'outfile_name': '',
                   'outfile_url': '', 'num_parts': '', 'num_combin': ''})


# @login_required(login_url="/accounts/login/")
def moclo(request):
    context = {}
    if request.method == "POST":
        if len(request.FILES) != 0:
            upload_file = request.FILES['upload_file']
            upload_db = request.FILES['upload_db']
            fs = FileSystemStorage()
            name_file = fs.save(upload_file.name, upload_file)
            name_db = fs.save(upload_db.name, upload_db)
            context['url_file'] = fs.url(name_file)
            context['url_db'] = fs.url(name_db)
            url_file = fs.url(name_file)
            url_db = fs.url(name_db)

            """Dispenser parameters"""
            machine = request.POST['machine']
            min_vol = request.POST['min_vol']
            vol_resol = request.POST['vol_resol']
            dead_vol = request.POST['dead_vol']
            dispenser_parameters = machine, float(min_vol) * 1e-9, float(vol_resol) * 1e-9, float(dead_vol)

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

                return render(request, 'moclo.html', {'uploadfile_name': upload_file, 'upload_db': upload_db, 'url_file': url_file, 'url_db': url_db,
                                                      'outfile_mantis_name': outfile_mantis_name, 'outfile_robot_name': outfile_robot_name,
                                                      'outfile_mantis_url': outfile_mantis_url, 'outfile_robot_url': outfile_robot_url, 'alerts': alerts, 'mixer_recipe': mixer_recipe, 'chip_mantis': chip_mantis})
            else:
                return render(request, 'moclo.html',
                              {'uploadfile_name': upload_file, 'upload_db': upload_db, 'url_file': url_file,
                               'url_db': url_db,
                               'outfile_mantis_name': '', 'outfile_robot_name': '',
                               'outfile_mantis_url': '', 'outfile_robot_url': '',
                               'alerts': alerts, 'mixer_recipe': '', 'chip_mantis': ''})

    return render(request, 'moclo.html')


# @login_required(login_url="/accounts/login/")
def about(request):
    return render(request, 'under_construction.html')




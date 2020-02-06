import os

from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from db.models import Project, Plate
from scripts.forms import NameForm

from libs.function import spotting, combinatorial, moclo, moclo_db, pcr_db, dnacauldron


def upload_file(request, filename):
    upload = request.FILES[filename]
    fs = FileSystemStorage()
    name = fs.save(upload.name, upload)
    url = fs.url(name)
    return upload, fs, name, url


def spotting_view(request):
    context = {}
    if request.method == "POST":
        user = request.user
        num_sources = request.POST['num_sources']
        num_well = request.POST['num_well']
        num_pattern = request.POST['num_pattern']
        pattern = request.POST['pattern']
        ''' Calling Python Script'''
        outfile, worklist, alert = spotting.run(int(num_sources), int(num_well), int(num_pattern), int(pattern), user)

        if alert is not None:
            return render(request, 'scripts/spotting.html', {'outfile': '', 'worklist': '', 'alert': alert})
        else:
            return render(request, 'scripts/spotting.html', {'outfile': outfile, 'worklist': worklist})
    return render(request, 'scripts/spotting.html', {'outfile': '', 'worklist': ''})


# @login_required(login_url="/accounts/login/")
def combinatorial_view(request):
    if request.method == "POST":
        user = request.user
        if len(request.FILES) != 0:
            upload, fs, name, url = upload_file(request, 'myFile')

            ''' Calling Python Script'''
            outfile, list_num_parts, list_num_combinations = combinatorial.run(settings.MEDIA_ROOT, name, user)
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
def moclo_view(request):
    if request.method == "POST":
        user = request.user
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
            alerts, outfile_mantis, outfile_robot, mixer_recipe, chip_mantis = \
                moclo.run(settings.MEDIA_ROOT, name_file, name_db, dispenser_parameters, mix_parameters, int(num_well_destination), int(pattern), mantis_two_chips, user)

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
def moclo_db_view(request):
    user = request.user
    projects = Project.objects.filter(collaborators=user)
    plates = Plate.objects.filter(project__in=projects)

    if request.method == "POST":
        if len(request.FILES) != 0:
            upload, fs, name_file, url_file = upload_file(request, 'upload_file')
            plate_content = request.POST['plate_content']
            plate_project = request.POST['plate_project']
            plate_ids = request.POST.get('plate_ids')
            plate_filters = plate_content, plate_project, plate_ids

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
            remove_outer_wells = 'remove_outer_wells' in request.POST
            dest_plate_parameters = int(num_well_destination), int(pattern), remove_outer_wells

            ''' Calling Python Script'''
            alerts, outfile_mantis, outfile_robot, mixer_recipe, chip_mantis = moclo_db.run(
                settings.MEDIA_ROOT, name_file, plate_filters, dispenser_parameters, mix_parameters,
                dest_plate_parameters, mantis_two_chips, user)

            if mixer_recipe is not None:
                return render(request, 'scripts/moclo_db.html', {'uploadfile_name': upload, 'url_file': url_file,
                                                      'outfile_mantis': outfile_mantis, 'outfile_robot': outfile_robot,
                                                      'alerts': alerts, 'mixer_recipe': mixer_recipe,
                                                     'chip_mantis': chip_mantis, 'projects': projects, 'plates': plates})
            else:
                return render(request, 'scripts/moclo_db.html',
                              {'uploadfile_name': upload, 'url_file': url_file,
                               'outfile_mantis': '', 'outfile_robot': '',
                               'alerts': alerts, 'mixer_recipe': '', 'chip_mantis': '',
                               'projects': projects, 'plates': plates})
    return render(request, 'scripts/moclo_db.html', {'projects': projects, 'plates': plates})


@login_required(login_url="/accounts/login/")
def pcr_db_view(request):
    if request.method == "POST":
        scriptname = 'Script PCR_DB'
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
            per_phusion = request.POST['phusion']
            per_buffer = request.POST['buffer']
            per_dntps = request.POST['dntps']
            total_vol = request.POST['total_vol']
            mantis_two_chips = 'mantis_two_chips' in request.POST
            add_water = 'add_water' in request.POST
            mix_parameters = \
                float(template_conc), \
                float(primer_f), \
                float(primer_r), \
                float(per_buffer), \
                float(per_phusion), \
                float(per_dntps), \
                float(total_vol), \
                add_water

            """Destination plate"""
            num_well_destination = request.POST['num_well_destination']
            pattern = request.POST['pattern']

            ''' Calling Python Script'''
            alerts, outfile_mantis, outfile_robot, mixer_recipe, chip_mantis = pcr_db.run(settings.MEDIA_ROOT,
                  name_file, dispenser_parameters, mix_parameters, int(num_well_destination), int(pattern), mantis_two_chips, user, scriptname)

            if mixer_recipe is not None:
                return render(request, 'scripts/pcr_db.html', {'uploadfile_name': upload, 'url_file': url_file,
                                                      'outfile_mantis': outfile_mantis, 'outfile_robot': outfile_robot,
                                                      'alerts': alerts, 'mixer_recipe': mixer_recipe, 'chip_mantis': chip_mantis})
            else:
                return render(request, 'scripts/pcr_db.html',
                              {'uploadfile_name': upload, 'url_file': url_file,
                               'outfile_mantis': '', 'outfile_robot': '',
                               'alerts': alerts, 'mixer_recipe': '', 'chip_mantis': ''})
    return render(request, 'scripts/pcr_db.html')


# @login_required(login_url="/accounts/login/")
def dnacauldron_view(request):
    if request.method == "POST":
        user = request.user
        form = NameForm(request.POST, request.FILES)
        Post = True
        data = form.cleaned_data.get('data')
        file = data['in_file']
        if form.is_valid():
        # if len(request.FILES) != 0:
        #     upload, fs, name, url = upload_file(request, 'myFile')
        #     upload_zip, fs_zip, name_zip, url_zip = upload_file(request, 'myzipFile')
        #     enzyme = request.POST['enzyme']
        #     topology = request.POST['topology']
            in_file = form.cleaned_data['in_file']
            zip_file = form.cleaned_data['zip_file']
            topology = form.cleaned_data['topology']
            enzyme = form.cleaned_data['enzyme']

            '''Calling Python Script'''
            alerts, out_zip = dnacauldron.run(settings.MEDIA_ROOT, in_file, zip_file, topology, enzyme, user)

            content = {
                'form': form,
                # 'url_file': url,
                # 'upload': upload,
                # 'url_zip': url_zip,
                # 'upload_zip': upload_zip,
                'alerts': alerts,
                'out_zip': out_zip,
            }
            return render(request, 'scripts/dnacauldron.html', content)
        else:
            print('form not valid')
    else:
        form = NameForm()

    return render(request, 'scripts/dnacauldron.html', {'form': form})
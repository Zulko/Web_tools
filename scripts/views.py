import os

from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required

from db.models import Project, Plate

from misc.forms import DestinationPlateForm, InputFileForm
from scripts.forms import (
    CauldronForm, PlateFilterForm, DispenserForm, MocloReactionParametersForm
)
from libs.function import (
    moclo, moclo_db, pcr_db, dnacauldron, echo_transfer, echo_transfer_db
)


def upload_file(request, filename):
    upload = request.FILES[filename]
    fs = FileSystemStorage()
    name = fs.save(upload.name, upload)
    url = fs.url(name)
    return upload, fs, name, url


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
    form_inputfile = InputFileForm()
    form_platefilter = PlateFilterForm()
    form_dispenser = DispenserForm()
    form_mocloreaction = MocloReactionParametersForm()
    form_destinationplate = DestinationPlateForm()

    if request.method == "POST":
        form_inputfile = InputFileForm(request.POST, request.FILES)
        form_platefilter = PlateFilterForm(request.POST)
        form_dispenser = DispenserForm(request.POST)
        form_mocloreaction = MocloReactionParametersForm(request.POST)
        form_destinationplate = DestinationPlateForm(request.POST)

        if form_inputfile.is_valid() and form_platefilter.is_valid() and form_dispenser.is_valid() and form_mocloreaction.is_valid() and form_destinationplate.is_valid():

            '''Input file'''
            upload, fs, name_file, url_file = upload_file(request, 'in_file')

            '''Plate filters'''
            content = form_platefilter.cleaned_data['content']
            project = form_platefilter.cleaned_data['project']
            plate_ids = form_platefilter.cleaned_data['plate_ids']
            plate_filters = content, project, plate_ids

            '''Dispenser'''
            machine = form_dispenser.cleaned_data['machine']
            min_vol = float(form_dispenser.cleaned_data['min_vol']) * 1e-3
            vol_resolution = float(form_dispenser.cleaned_data['vol_resolution']) * 1e-3
            dead_vol = float(form_dispenser.cleaned_data['dead_vol'])
            dispenser_parameters = machine, min_vol, vol_resolution, dead_vol

            '''Reaction parameters'''
            part_fmol = float(form_mocloreaction.cleaned_data['part_fmol'])
            bb_fmol = float(form_mocloreaction.cleaned_data['bb_fmol'])
            total_volume = float(form_mocloreaction.cleaned_data['total_volume'])
            buffer_per = float(form_mocloreaction.cleaned_data['buffer_per'])
            rest_enz_perc = float(form_mocloreaction.cleaned_data['rest_enz_perc'])
            ligase_per = float(form_mocloreaction.cleaned_data['ligase_per'])
            add_water = form_mocloreaction.cleaned_data['add_water']
            mantis_two_chips = form_mocloreaction.cleaned_data['mantis_two_chips']
            mix_parameters = part_fmol, bb_fmol, total_volume, buffer_per, rest_enz_perc, ligase_per, add_water

            '''Destination plate'''
            num_wells = int(form_destinationplate.cleaned_data['num_wells'])
            filled_by = int(form_destinationplate.cleaned_data['filled_by'])
            remove_outer_wells = form_destinationplate.cleaned_data['remove_outer_wells']
            dest_plate_parameters = num_wells, filled_by, remove_outer_wells

            ''' Calling Python Script: Moclo_db or New Golden Gate_db'''
            alerts, outfile_mantis, outfile_robot, mixer_recipe, chip_mantis = moclo_db.run(
                settings.MEDIA_ROOT, name_file, plate_filters, dispenser_parameters, mix_parameters,
                dest_plate_parameters, mantis_two_chips, user)

            if mixer_recipe is not None:
                content = {
                    'form_inputfile': form_inputfile,
                    'form_dispenser': form_dispenser,
                    'form_platefilter': form_platefilter,
                    'form_mocloreaction': form_mocloreaction,
                    'form_destinationplate': form_destinationplate,
                    'projects': projects,
                    'plates': plates,
                    'uploadfile_name': upload,
                    'url_file': url_file,
                    'outfile_mantis': outfile_mantis,
                    'outfile_robot': outfile_robot,
                    'alerts': alerts,
                    'mixer_recipe': mixer_recipe,
                    'chip_mantis': chip_mantis,
                }
                return render(request, 'scripts/moclo_db.html', content)
            else:
                content = {
                    'form_inputfile': form_inputfile,
                    'form_dispenser': form_dispenser,
                    'form_platefilter': form_platefilter,
                    'form_mocloreaction': form_mocloreaction,
                    'form_destinationplate': form_destinationplate,
                    'uploadfile_name': upload,
                    'url_file': url_file,
                    'outfile_mantis': '',
                    'outfile_robot': '',
                    'alerts': alerts,
                    'mixer_recipe': '',
                    'chip_mantis': '',
                    'projects': projects,
                    'plates': plates,

                }
                return render(request, 'scripts/moclo_db.html', content)
        else:
            print('form not valid')

    content = {
        'form_inputfile': form_inputfile,
        'form_dispenser': form_dispenser,
        'form_platefilter': form_platefilter,
        'form_mocloreaction': form_mocloreaction,
        'form_destinationplate': form_destinationplate,
        'projects': projects,
        'plates': plates,
    }
    return render(request, 'scripts/moclo_db.html', content)


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
        form = CauldronForm(request.POST, request.FILES)
        if form.is_valid():
            upload, fs, name_file, url_file = upload_file(request, 'in_file')
            upload_zip, fs_zip, name_zipfile, url_zip = upload_file(request, 'zip_file')
            topology = form.cleaned_data['topology']
            enzyme = form.cleaned_data['enzyme']

            '''Calling Python Script'''
            alerts, out_zip = dnacauldron.run(settings.MEDIA_ROOT, name_file, name_zipfile, topology, enzyme, user)

            content = {
                'form': form,
                'url_file': url_file,
                'upload': upload,
                'url_zip': url_zip,
                'upload_zip': upload_zip,
                'alerts': alerts,
                'out_zip': out_zip,
            }
            return render(request, 'scripts/dnacauldron.html', content)
        else:
            print('form not valid')
    else:
        form = CauldronForm()

    return render(request, 'scripts/dnacauldron.html', {'form': form})


def echo_transfer_view(request):
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

            """Destination plate"""
            num_well_destination = request.POST['num_well_destination']
            pattern = request.POST['pattern']
            remove_outer_wells = 'remove_outer_wells' in request.POST
            dest_plate_parameters = int(num_well_destination), int(pattern), remove_outer_wells

            ''' Calling Python Script'''
            alerts, outfile_robot = \
                echo_transfer.run(settings.MEDIA_ROOT, name_file, name_db, dispenser_parameters, dest_plate_parameters, user, scriptname='Echo Transfer')

            if outfile_robot is not None:
                outfile_robot_name = os.path.basename(outfile_robot.name)
                outfile_robot_url = fs.url(outfile_robot_name)
                return render(request, 'scripts/echo_transfer.html',
                              {'uploadfile_name': upload_f, 'upload_db': upload_db, 'url_file': url_file,
                               'url_db': url_db, 'outfile_robot_name': outfile_robot_name,
                               'outfile_robot_url': outfile_robot_url, 'alerts': alerts})
            else:
                return render(request, 'scripts/echo_transfer.html',
                              {'uploadfile_name': upload_f, 'upload_db': upload_db, 'url_file': url_file,
                               'url_db': url_db, 'outfile_mantis_name': '', 'outfile_robot_name': '',
                               'outfile_robot_url': '', 'alerts': alerts})
    return render(request, 'scripts/echo_transfer.html')


@login_required(login_url="/accounts/login/")
def echo_transfer_db_view(request):
    user = request.user
    projects = Project.objects.filter(collaborators=user)
    plates = Plate.objects.filter(project__in=projects)

    form_inputfile = InputFileForm()
    form_platefilter = PlateFilterForm()
    form_dispenser = DispenserForm()
    form_destinationplate = DestinationPlateForm()

    if request.method == "POST":
        scriptname = 'Echo Transfer from Worklist'
        form_inputfile = InputFileForm(request.POST, request.FILES)
        form_platefilter = PlateFilterForm(request.POST)
        form_dispenser = DispenserForm(request.POST)
        form_destinationplate = DestinationPlateForm(request.POST)

        if form_inputfile.is_valid() and form_platefilter.is_valid() and form_dispenser.is_valid() and form_destinationplate.is_valid():
            '''Input file'''
            upload, fs, name_file, url_file = upload_file(request, 'in_file')

            '''Plate filters'''
            content = form_platefilter.cleaned_data['content']
            project = form_platefilter.cleaned_data['project']
            plate_ids = form_platefilter.cleaned_data['plate_ids']
            plate_filters = content, project, plate_ids

            '''Dispenser'''
            machine = form_dispenser.cleaned_data['machine']
            min_vol = float(form_dispenser.cleaned_data['min_vol']) * 1e-3
            vol_resolution = float(form_dispenser.cleaned_data['vol_resolution']) * 1e-3
            dead_vol = float(form_dispenser.cleaned_data['dead_vol'])
            dispenser_parameters = machine, min_vol, vol_resolution, dead_vol

            '''Destination plate'''
            num_wells = int(form_destinationplate.cleaned_data['num_wells'])
            filled_by = int(form_destinationplate.cleaned_data['filled_by'])
            remove_outer_wells = form_destinationplate.cleaned_data['remove_outer_wells']
            dest_plate_parameters = num_wells, filled_by, remove_outer_wells

            ''' Calling Python Script'''
            alerts, outfile_robot = echo_transfer_db.run(
                settings.MEDIA_ROOT, name_file, plate_filters, dispenser_parameters, dest_plate_parameters, user, scriptname)
            print(len(alerts))
            if len(alerts) == 0:
                content = {
                    'form_inputfile': form_inputfile,
                    'form_dispenser': form_dispenser,
                    'form_platefilter': form_platefilter,
                    'form_destinationplate': form_destinationplate,
                    'uploadfile_name': upload,
                    'url_file': url_file,
                    'outfile_robot': outfile_robot,
                    'alerts': alerts,
                    'projects': projects,
                    'plates': plates
                }
                return render(request, 'scripts/echo_transfer_db.html', content)
            else:
                content = {
                    'form_inputfile': form_inputfile,
                    'form_dispenser': form_dispenser,
                    'form_platefilter': form_platefilter,
                    'form_destinationplate': form_destinationplate,
                    'uploadfile_name': None,
                    'url_file': None,
                    'outfile_robot': None,
                    'alerts': alerts,
                    'projects': projects,
                    'plates': plates
                }
                return render(request, 'scripts/echo_transfer_db.html', content)

    content = {
        'form_inputfile': form_inputfile,
        'form_dispenser': form_dispenser,
        'form_platefilter': form_platefilter,
        'form_destinationplate': form_destinationplate,
        'uploadfile_name': None,
        'url_file': None,
        'outfile_robot': None,
        'alerts': None,
        'projects': projects,
        'plates': plates,
    }

    return render(request, 'scripts/echo_transfer_db.html', content)
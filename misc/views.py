import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from db.models import Project, Plate
from misc.forms import DotPlateForm, DestinationPlateForm

from libs.function import normalization, fasta2primer3
from libs.misc import genbank, nrc_sequence, echo_transfer_db, echo_transfer, plate_creator


def upload_file(request, filename):
    upload = request.FILES[filename]
    fs = FileSystemStorage()
    name = fs.save(upload.name, upload)
    url = fs.url(name)
    return upload, fs, name, url


def genbank_view(request):
    if request.method == "POST":
        user = request.user
        if len(request.FILES) != 0:
            upload, fs, name, url = upload_file(request, 'myFile')

            ''' Calling Python Script'''
            outfile = genbank.generate_from_csv(settings.MEDIA_ROOT, name, user)
            if outfile is not None:
                return render(request, 'misc/genbank.html',
                              {'uploadfile_name': upload.name, 'url': url, 'outfile': outfile})

    return render(request, 'misc/genbank.html',
                  {'uploadfile_name': '', 'url': '', 'outfile_name': '', 'outfile_url': ''})


def primer_view(request):
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
            outfile, alert = fasta2primer3.run(settings.MEDIA_ROOT, name, start_prime, end_prime, size_min_prime,
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


def normalization_view(request):
    if request.method == "POST":
        user = request.user
        if len(request.FILES) != 0:
            upload, fs, name, url = upload_file(request, 'upload_file')
            in_well = request.POST['num_well_source']
            out_well = request.POST['num_well_destination']
            bb_fmol = request.POST['bb_fmol']
            part_fmol = request.POST['part_fmol']

            ''' Calling Python Script'''
            outfile, alert = normalization.run(settings.MEDIA_ROOT, name, int(in_well), int(out_well), int(bb_fmol), int(part_fmol), user)
            if outfile is not None:
                outfile_name = str(outfile)
                outfile_url = fs.url(outfile_name)
                return render(request, 'misc/normalization.html', {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name, 'outfile_url': outfile_url, 'alert':alert})
            else:
                return render(request, 'misc/normalization.html',
                              {'uploadfile_name': upload.name, 'url': url, 'outfile_name': '',
                               'outfile_url': '', 'alert': alert})
    return render(request, 'misc/normalization.html', {'uploadfile_name': '', 'url': '', 'outfile_name': '', 'outfile_url': '', 'alert': ''})


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
                return render(request, 'misc/echo_transfer.html',
                              {'uploadfile_name': upload_f, 'upload_db': upload_db, 'url_file': url_file,
                               'url_db': url_db, 'outfile_robot_name': outfile_robot_name,
                               'outfile_robot_url': outfile_robot_url, 'alerts': alerts})
            else:
                return render(request, 'misc/echo_transfer.html',
                              {'uploadfile_name': upload_f, 'upload_db': upload_db, 'url_file': url_file,
                               'url_db': url_db, 'outfile_mantis_name': '', 'outfile_robot_name': '',
                               'outfile_robot_url': '', 'alerts': alerts})
    return render(request, 'misc/echo_transfer.html')


@login_required(login_url="/accounts/login/")
def echo_transfer_db_view(request):
    user = request.user
    projects = Project.objects.filter(collaborators=user)
    plates = Plate.objects.filter(project__in=projects)

    if request.method == "POST":
        scriptname = 'Echo Transfer from Worklist'
        user = request.user
        if len(request.FILES) > 0:
            upload_p, fs_p, name_file_p, url_file_p = upload_file(request, 'upload_file_parts')
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

            """Destination plate"""
            num_well_destination = request.POST['num_well_destination']
            pattern = request.POST['pattern']
            remove_outer_wells = 'remove_outer_wells' in request.POST
            dest_plate_parameters = int(num_well_destination), int(pattern), remove_outer_wells

            ''' Calling Python Script'''
            alerts, outfile_robot = echo_transfer_db.run(
                settings.MEDIA_ROOT,
                name_file_p,
                plate_filters,
                dispenser_parameters,
                dest_plate_parameters,
                user,
                scriptname
            )
            print(len(alerts))
            if len(alerts) == 0:
                context = {
                    'uploadfile_name': upload_p,
                    'url_file': url_file_p,
                    'outfile_robot': outfile_robot,
                    'alerts': alerts,
                    'projects': projects,
                    'plates': plates
                }
                return render(request, 'misc/echo_transfer_db.html', context)
            else:
                context = {
                    'uploadfile_name': None,
                    'url_file': None,
                    'outfile_robot': None,
                    'alerts': alerts,
                    'projects': projects,
                    'plates': plates
                }
                return render(request, 'misc/echo_transfer_db.html', context)
        else:
            alerts = ['Missing input file']
            context = {
                'uploadfile_name': None,
                'url_file': None,
                'outfile_robot': None,
                'alerts': alerts,
                'projects': projects,
                'plates': plates
            }
            return render(request, 'misc/echo_transfer_db.html', context)
    return render(request, 'misc/echo_transfer_db.html', {'projects': projects, 'plates':plates})


def dot_plate_view(request):
    user = request.user
    if request.method == "POST":
        form_plate = DotPlateForm(request.POST)
        form_destinationplate = DestinationPlateForm(request.POST)

        if form_plate.is_valid() and form_destinationplate.is_valid():
            '''Select plate'''
            id = form_plate.cleaned_data['plate_name']
            num_dots = int(form_plate.cleaned_data['num_dots'])
            dot_vol = int(form_plate.cleaned_data['dot_vol'])

            '''Destination plate'''
            num_wells = int(form_destinationplate.cleaned_data['num_wells'])
            filled_by = int(form_destinationplate.cleaned_data['filled_by'])
            remove_outer_wells = form_destinationplate.cleaned_data['remove_outer_wells']

            ''' Calling Python Script'''
            out_file = plate_creator.run_dot_plate(settings.MEDIA_ROOT, id, num_dots, dot_vol, num_wells, filled_by, remove_outer_wells, user)

            context = {
                'outfile_robot': out_file,
                'form_plate': form_plate,
                'form_dest_plate': form_destinationplate,
            }

            return render(request, 'misc/dot_plate.html', context)

    form_plate = DotPlateForm()
    form_destinationplate = DestinationPlateForm()

    context = {
        'form_plate': form_plate,
        'form_dest_plate': form_destinationplate,
    }

    return render(request, 'misc/dot_plate.html', context)
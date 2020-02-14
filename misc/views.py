import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from db.models import Project, Plate
from misc.forms import DotPlateForm, DestinationPlateForm, InputFileForm

from libs.function import normalization, fasta2primer3
from libs.misc import genbank, plate_creator, combinatorial


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


# @login_required(login_url="/accounts/login/")
def combinatorial_view(request):
    form_inputfile = InputFileForm()

    if request.method == "POST":
        user = request.user
        form_inputfile = InputFileForm(request.POST, request.FILES)

        if form_inputfile.is_valid():
            upload, fs, name_file, url_file = upload_file(request, 'in_file')

            ''' Calling Python Script'''
            outfile, list_num_parts, list_num_combinations = combinatorial.run(settings.MEDIA_ROOT, name_file, user)
            if outfile is not None:
                outfile_name = os.path.basename(outfile.name)
                outfile_url = fs.url(outfile_name)

                content = {
                    'form_inputfile': form_inputfile,
                    'uploadfile_name': upload.name,
                    'url': url_file,
                    'outfile_name': outfile_name,
                    'outfile_url': outfile_url,
                    'num_parts': list_num_parts,
                    'num_combin': list_num_combinations,
                }
                return render(request, 'misc/combinatorial.html', content)
            # else:
            #     return render(request, 'misc/combinatorial.html',
            #                   {'uploadfile_name': '', 'url': '', 'outfile_name': '',
            #                    'outfile_url': '', 'num_parts': '', 'num_combin': ''})

    content = {
        'form_inputfile': form_inputfile,
        'uploadfile_name': '',
        'url': '',
        'outfile_name': '',
        'outfile_url': '',
        'num_parts': '',
        'num_combin': ''
    }
    return render(request, 'misc/combinatorial.html', content)
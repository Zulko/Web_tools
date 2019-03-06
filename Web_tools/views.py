from django.http import HttpResponse
from django.shortcuts import render
from libs.function.spotting import run_spotting
from libs.function.normalization import run_normalization
from libs.function.fasta2primer3 import run_primer
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
            ''' Calling Python Script'''
            outfile = run_normalization(settings.MEDIA_ROOT, name, int(in_well), int(out_well))
            if outfile is not None:
                outfile_name = os.path.basename(outfile.name)
                outfile_url = fs.url(outfile_name)
                return render(request, 'normalization.html', {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name,'outfile_url': outfile_url})
    return render(request, 'normalization.html', {'uploadfile_name': '', 'url': '', 'outfile_name': '','outfile_url': ''})


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
    return render(request, 'combinatorial.html')


# @login_required(login_url="/accounts/login/")
def about(request):
    return render(request, 'under_construction.html')




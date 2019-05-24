from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render

from libs.misc.genbank import generate_from_csv
from libs.function.fasta2primer3 import run_primer

import os


def genbank(request):
    if request.method == "POST":
        if len(request.FILES) != 0:
            upload = request.FILES['myFile']
            fs = FileSystemStorage()
            name = fs.save(upload.name, upload)
            url = fs.url(name)
            ''' Calling Python Script'''
            outfile = generate_from_csv(settings.MEDIA_ROOT, name)
            if outfile is not None:
                outfile_name = os.path.basename(outfile.filename)
                outfile_url = fs.url(outfile_name)
                return render(request, 'misc/genbank.html',
                              {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name,
                               'outfile_url': outfile_url})

    return render(request, 'misc/genbank.html',
                  {'uploadfile_name': '', 'url': '', 'outfile_name': '', 'outfile_url': ''})


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
                return render(request, 'misc/primer.html', {'uploadfile_name': upload.name, 'url': url, 'outfile_name': outfile_name, 'outfile_url': outfile_url})
        else:
            return render(request, 'misc/primer.html', {'uploadfile_name': '', 'url': '', 'outfile_name': 'Missing an Input File', 'abs_path': ''})
    return render(request, 'misc/primer.html', {'uploadfile_name': '', 'url': '', 'outfile_name': '', 'abs_path': ''})

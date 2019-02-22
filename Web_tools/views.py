from django.http import HttpResponse
from django.shortcuts import render
from libs.function.spotting import run_spotting


def home(request):
    return render(request, 'home.html')


def spoting(request):
    if request.method == "POST":
        num_sources = request.POST['num_sources']
        num_well = request.POST['num_well']
        num_pattern = request.POST['num_pattern']
        pattern = request.POST['pattern']
        outfile_name, abs_path = run_spotting(int(num_sources), int(num_well), int(num_pattern), int(pattern))
        return render(request, 'spoting.html', {'outfile_name': outfile_name,'abs_path': abs_path})
    return render(request, 'spoting.html', {'outfile_name':'', 'abs_path':''})


def normalization(request):
    return render(request, 'normalization.html')


def primer(request):
    return render(request, 'primer.html')


def about(request):
    return render(request, 'about.html')


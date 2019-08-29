from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Experiment

# Create your views here.


@login_required()
def design_view(request):
    all_experiments = Experiment.objects.all()

    context = {
        "all_experiments": all_experiments,
    }
    return render(request, 'design/index.html', context)

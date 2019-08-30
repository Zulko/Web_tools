from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Experiment
from .forms import ExperimentForm, StepForm

# Create your views here.


@login_required()
def design_view(request):
    all_experiments = Experiment.objects.all()
    formExperimentAdd = ExperimentForm()
    formStepAdd = StepForm()

    context = {
        'form_experiment_add': formExperimentAdd,
        'form_step_add': formStepAdd,
        'all_experiments': all_experiments,
    }
    return render(request, 'design/index.html', context)


@login_required()
def experiment_add(request):
    all_experiments = Experiment.objects.all()
    formExperimentAdd = ExperimentForm()
    formStepAdd = StepForm()

    context = {
        'form_experiment_add': formExperimentAdd,
        'form_step_add': formStepAdd,
        'all_experiments': all_experiments,
    }
    return render(request, 'design/index.html', context)


@login_required()
def step_add(request):
    all_experiments = Experiment.objects.all()
    formExperimentAdd = ExperimentForm()
    formStepAdd = StepForm()

    context = {
        'form_experiment_add': formExperimentAdd,
        'form_step_add': formStepAdd,
        'all_experiments': all_experiments,
    }
    return render(request, 'design/index.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Experiment
from .forms import ExperimentForm, StepForm

# Create your views here.


@login_required()
def design_view(request):
    print('design_view')
    user = request.user
    all_experiments = Experiment.objects.all()
    formExperimentAdd = ExperimentForm(initial={'author': user})
    formExperimentUpdate = ExperimentForm(initial={'author': user})
    formStepAdd = StepForm()

    if 'submit_add_experiment' in request.POST:
        print('design_view: submit_add_experiment')
        formExperimentAdd = ExperimentForm(request.POST, initial={'author': user})
        if formExperimentAdd.is_valid():
            formExperimentAdd.save()
            return redirect('design:design_view')

    elif 'submit_add_step' in request.POST:
        print('design_view: submit_add_step')
        formStepAdd = StepForm(request.POST, request.FILES)
        if formStepAdd.is_valid():
            print('form valid')
            formStepAdd.save()
            return redirect('design:design_view')
        else:
            print('form invalid')

    context = {
        'form_experiment_add': formExperimentAdd,
        'form_experiment_update': formExperimentUpdate,
        'form_step_add': formStepAdd,
        'all_experiments': all_experiments,
    }
    return render(request, 'design/index.html', context)


@login_required()
def experiment_view(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    formExperimentUpdate = ExperimentForm(instance=experiment)

    if 'submit_update_experiment' in request.POST:
        print('found the form update')
        formExperimentUpdate = ExperimentForm(request.POST,  instance=experiment)
        if formExperimentUpdate.is_valid():
            formExperimentUpdate.save()
            return redirect('design:experiment_view', experiment.id)
        else:
            print('form is not valid')

    context = {
        'experiment': experiment,
        'form_experiment_update': formExperimentUpdate,
    }
    return render(request, 'design/experiment.html', context)


@login_required()
def experiment_add(request):
    user = request.user
    all_experiments = Experiment.objects.all()
    formExperimentAdd = ExperimentForm(initial={'author': user})
    formExperimentUpdate = ExperimentForm(initial={'author': user})
    formStepAdd = StepForm()

    if 'submit_add_experiment' in request.POST:
        formExperimentAdd = ExperimentForm(request.POST, initial={'author': user})
        if formExperimentAdd.is_valid():
            formExperimentAdd.save()
            return redirect('design:design_view')

    elif 'submit_add_step' in request.POST:
        formStepAdd = StepForm(request.POST)
        if formStepAdd.is_valid():
            formStepAdd.save()
            return redirect('design:design_view')

    context = {
        'form_experiment_add': formExperimentAdd,
        'form_experiment_update': formExperimentUpdate,
        'form_step_add': formStepAdd,
        'all_experiments': all_experiments,
    }
    return render(request, 'design/index.html', context)


@login_required()
def experiment_delete(request, experiment_id):
    if request.method == 'POST':
        experiment = get_object_or_404(Experiment, id=experiment_id)
        experiment.delete()
    return redirect('design:design_view')


@login_required()
def experiment_update(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    if 'submit_update_experiment' in request.POST:
        formExperimentUpdate = ExperimentForm(request.POST, instance=experiment)
        if formExperimentUpdate.is_valid():
            formExperimentUpdate.save()
            return redirect('design:experiment_view', experiment.id)
    else:
        formExperimentUpdate = ExperimentForm(instance=experiment)

    context = {
        'form_experiment_update': formExperimentUpdate
    }

    return render(request,'design/experiment.html', context)


@login_required()
def step_add(request):
    all_experiments = Experiment.objects.all()
    formExperimentAdd = ExperimentForm()
    formStepAdd = StepForm()

    if 'submit_add_step' in request.POST:
        formStepAdd = StepForm(request.POST)
        if formStepAdd.is_valid():
            formStepAdd.save()
            return redirect('design:design_view')

    context = {
        'form_experiment_add': formExperimentAdd,
        'form_step_add': formStepAdd,
        'all_experiments': all_experiments,
    }
    return render(request, 'design/index.html', context)

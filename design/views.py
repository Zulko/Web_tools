from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Experiment, Step
from .forms import ExperimentForm, StepForm

# Create your views here.


@login_required()
def design_view(request):
    print('design_view')
    user = request.user
    all_experiments = Experiment.objects.all()
    all_steps = Step.objects.all()
    formExperimentAdd = ExperimentForm(initial={'author': user})
    formExperimentUpdate = ExperimentForm(initial={'author': user})
    formStepAdd = StepForm()

    if 'submit_add_experiment' in request.POST:
        print('design_view: submit_add_experiment')
        formExperimentAdd = ExperimentForm(request.POST, request.FILES, initial={'author': user})
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
        'all_steps': all_steps,
    }
    return render(request, 'design/index.html', context)


@login_required()
def experiment_view(request, experiment_id):
    print('experiment_view')
    experiment = get_object_or_404(Experiment, id=experiment_id)
    all_steps = Step.objects.filter(experiment_id=experiment.id)
    formExperimentUpdate = ExperimentForm(instance=experiment)
    formStepAdd = StepForm(initial={'experiment': experiment})
    formStepUpdate = StepForm(initial={'experiment': experiment})

    if 'submit_update_experiment' in request.POST:
        print('found the form update')
        formExperimentUpdate = ExperimentForm(request.POST, request.FILES, instance=experiment)
        if formExperimentUpdate.is_valid():
            formExperimentUpdate.save()
            return redirect('design:experiment_view', experiment.id)

    elif 'submit_add_step' in request.POST:
        print('try add step')
        formStepAdd = StepForm(request.POST, request.FILES, initial={'experiment': experiment})
        if formStepAdd.is_valid():
            print('form is valid')
            formStepAdd.save()
            return redirect('design:experiment_view',  experiment.id)
        else:
            print('form is not valid')

    # elif 'submit_update_step' in request.POST:
    #     print('try to update')
    #     formStepUpdate = StepForm(request.POST, request.FILES)
    #     if formStepUpdate.is_valid():
    #         formStepUpdate.save()
    #         return redirect('design:experiment_view', experiment.id)


    context = {
        'all_steps': all_steps,
        'experiment': experiment,
        'form_experiment_update': formExperimentUpdate,
        'form_step_add': formStepAdd,
        'form_step_update': formStepUpdate,
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
        formExperimentAdd = ExperimentForm(request.POST, request.FILES, initial={'author': user})
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
    formStepAdd = StepForm()
    if 'submit_update_experiment' in request.POST:
        formExperimentUpdate = ExperimentForm(request.POST, request.FILES, instance=experiment)
        if formExperimentUpdate.is_valid():
            formExperimentUpdate.save()
            return redirect('design:experiment_view', experiment.id)
    else:
        formExperimentUpdate = ExperimentForm(instance=experiment)

    context = {
        'form_experiment_update': formExperimentUpdate,
        'form_step_add': formStepAdd,
    }

    return render(request, 'design/experiment.html', context)


@login_required()
def step_add(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    formExperimentUpdate = ExperimentForm(instance=experiment)
    formStepAdd = StepForm()

    if 'submit_add_step' in request.POST:
        formStepAdd = StepForm(request.POST)
        if formStepAdd.is_valid():
            formStepAdd.save()
            return redirect('design:experiment_view')

    context = {
        'form_experiment_update': formExperimentUpdate,
        'form_step_add': formStepAdd,
    }
    return render(request, 'design/index.html', context)


@login_required()
def step_view(request, experiment_id, step_id):
    print('step_view')
    experiment = get_object_or_404(Experiment, id=experiment_id)
    all_steps = Step.objects.filter(experiment_id=experiment.id).order_by('-id').reverse()
    step = get_object_or_404(Step, id=step_id)
    formExperimentUpdate = ExperimentForm(instance=experiment)
    formStepAdd = StepForm(initial={'experiment': experiment})
    formStepUpdate = StepForm(instance=step)

    if 'submit_update_experiment' in request.POST:
        print('found the form update')
        formExperimentUpdate = ExperimentForm(request.POST, request.FILES, instance=experiment)
        if formExperimentUpdate.is_valid():
            formExperimentUpdate.save()
            return redirect('design:experiment_view', experiment.id)

    elif 'submit_add_step' in request.POST:
        print('try add step')
        formStepAdd = StepForm(request.POST, request.FILES, initial={'experiment': experiment})
        if formStepAdd.is_valid():
            print('form is valid')
            step = formStepAdd.save()
            return redirect('design:step_view', experiment.id, step.id)
        else:
            print('form is not valid')

    elif 'submit_update_step' in request.POST:
        print('try to update')
        formStepUpdate = StepForm(request.POST, request.FILES, instance=step)
        if formStepUpdate.is_valid():
            formStepUpdate.save()
            return redirect('design:step_view', experiment.id, step.id)

    context = {
        'all_steps': all_steps,
        'step': step,
        'experiment': experiment,
        'form_experiment_update': formExperimentUpdate,
        'form_step_add': formStepAdd,
        'form_step_update': formStepUpdate,
    }

    return render(request, 'design/experiment.html', context)

@login_required()
def step_update(request, experiment_id, step_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    step = get_object_or_404(Step, id=step_id)
    formExperimentUpdate = ExperimentForm(instance=experiment)
    print('submit_update_step')
    if 'submit_update_step' in request.POST:
        formStepUpdate = StepForm(request.POST, request.FILES, instance=step)
        if formStepUpdate.is_valid():
            formStepUpdate.save()
            return redirect('design:experiment_view', experiment.id, step.id)
    else:
        formStepUpdate = StepForm(instance=step)

    context = {
        'form_experiment_update': formExperimentUpdate,
        'form_step_update': formStepUpdate,
    }

    return render(request, 'design/experiment.html', context)


@login_required()
def step_delete(request, experiment_id, step_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    step = get_object_or_404(Step, id=step_id)

    if request.method == 'POST':
        step.delete()

    return redirect('design:experiment_view', experiment.id)
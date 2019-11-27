import os

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import Experiment, Step
from .forms import ExperimentForm, StepForm

from db.models import File

from libs.function.spotting import run_spotting
from libs.function.pcr_db import run_pcr_db
from libs.misc import parser
from libs.biofoundry.db import save_file
from libs.misc import file
from libs.biofoundry import db

# Create your views here.


def upload_file(request, filename):
    upload = request.FILES[filename]
    fs = FileSystemStorage()
    name = fs.save(upload.name, upload)
    url = fs.url(name)
    return upload, fs, name, url


def delete_files(list_files):
    for file in list_files:
        file.delete()


def delete_plates(list_plates):
    for plate in list_plates:
        plate.delete()


@login_required()
def design_view(request):
    print('design_view')
    user = request.user
    all_experiments = Experiment.objects.all()
    all_steps = Step.objects.all().order_by('-id').reverse()
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
    all_steps = Step.objects.filter(experiment_id=experiment.id).order_by('-id').reverse()
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


def spotting_script(request, step, user):
    '''Clean the old files in step'''
    delete_files(step.output_files.all())
    delete_plates(step.output_plates.all())
    step.save()

    num_sources = request.POST['num_sources']
    num_well = request.POST['num_well']
    num_pattern = request.POST['num_pattern']
    pattern = request.POST['pattern']
    ''' Calling Python Script'''
    outfile, worklist, alert = run_spotting(int(num_sources), int(num_well), int(num_pattern), int(pattern),
                                            user)

    if outfile is not None:
        '''Add new files in step'''
        step.status_run = True
        step.output_files.add(outfile)
        step.output_files.add(worklist)
        step.save()

        '''Read outfile and Create destination plates'''
        plates_out = parser.create_plate_on_database(settings.MEDIA_ROOT, outfile, int(num_well), step)
        for plate in plates_out:
            step.output_plates.add(plate)
            plate.save()
        step.save()

        return outfile, worklist, alert
    else:
        return None, None, alert


def pcr_script(request, step, user):
    '''Clean the info and old files in step'''
    step.input_plates.clear()
    step.input_file_script = None
    step.instructions = ''
    delete_files(step.output_files.all())
    delete_plates(step.output_plates.all())
    step.save()

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
        alerts, outfile_mantis, outfile_robot, mixer_recipe, chip_mantis = run_pcr_db(settings.MEDIA_ROOT,
                                                                                      name_file, dispenser_parameters,
                                                                                      mix_parameters,
                                                                                      int(num_well_destination),
                                                                                      int(pattern), mantis_two_chips,
                                                                                      user, scriptname='Experiment:'+step.experiment.name)

        if mixer_recipe is not None:
            filein = File(name=name_file, script='Experiment:'+step.experiment.name, author=user, file=name_file)
            filein.save()
            step.status_run = True
            step.input_file_script = filein
            step.output_files.add(outfile_mantis)
            step.output_files.add(outfile_robot)
            for item in mixer_recipe:
                step.instructions += str(item[0]) + ': '+str(item[1]) + 'ul, '
            for item in chip_mantis:
                step.instructions += str(item[0]) + ': '+str(item[1]) + 'ul, '

            '''Gets the source plates used in the experiment'''
            plates_in = parser.list_plate_from_database(settings.MEDIA_ROOT, outfile_robot)
            for plate in plates_in:
                step.input_plates.add(plate)
                # plate.file =

            plates_out = parser.create_plate_on_database(settings.MEDIA_ROOT, outfile_robot, num_well_destination, step)
            for plate in plates_out:
                step.output_plates.add(plate)

            #Add file to save original values of source plate
            #reduce volume in source plates
            #create destination plates
            #list destination plates
            # create_destination_plates()

            step.save()
            return alerts, outfile_mantis, outfile_robot, mixer_recipe, chip_mantis
        else:
            return alerts, None, None, None, None
    else:
        alerts = ['Missing input file']
        return alerts, None, None, None, None


@login_required()
def step_view(request, experiment_id, step_id):
    user = request.user
    experiment = get_object_or_404(Experiment, id=experiment_id)
    all_steps = Step.objects.filter(experiment_id=experiment.id).order_by('-id').reverse()
    step = get_object_or_404(Step, id=step_id)
    formExperimentUpdate = ExperimentForm(instance=experiment)
    formStepAdd = StepForm(initial={'experiment': experiment})
    formStepUpdate = StepForm(instance=step)
    run_results = None

    if 'submit_update_experiment' in request.POST:
        formExperimentUpdate = ExperimentForm(request.POST, request.FILES, instance=experiment)
        if formExperimentUpdate.is_valid():
            formExperimentUpdate.save()
            return redirect('design:experiment_view', experiment.id)

    elif 'submit_add_step' in request.POST:
        formStepAdd = StepForm(request.POST, request.FILES, initial={'experiment': experiment})
        if formStepAdd.is_valid():
            step = formStepAdd.save()
            return redirect('design:step_view', experiment.id, step.id)
        else:
            print('form is not valid')

    elif 'submit_update_step' in request.POST:
        formStepUpdate = StepForm(request.POST, request.FILES, instance=step)
        if formStepUpdate.is_valid():
            formStepUpdate.save()
            return redirect('design:step_view', experiment.id, step.id)

    elif 'submit_run_step' in request.POST:
        if step.script == 'Spotting':
            outfile, worklist, alert = spotting_script(request, step, user)

            #Read outfile and create process plates
            context = {
                'all_steps': all_steps,
                'step': step,
                'experiment': experiment,
                'form_experiment_update': formExperimentUpdate,
                'form_step_add': formStepAdd,
                'form_step_update': formStepUpdate,
                'run_results': run_results,
                'outfile': outfile,
                'worklist': worklist,
                'alert': alert,
            }

            return render(request, 'design/experiment.html', context)

        elif step.script == 'PCR':
            print('PCR: Yes')
            alerts, outfile_mantis, outfile_robot, mixer_recipe, chip_mantis = pcr_script(request, step, user)

            context = {
                'all_steps': all_steps,
                'step': step,
                'experiment': experiment,
                'form_experiment_update': formExperimentUpdate,
                'form_step_add': formStepAdd,
                'form_step_update': formStepUpdate,
                'run_results': run_results,
                'outfile': outfile_mantis,
                'worklist': outfile_robot,
                'mixer_recipe': mixer_recipe,
                'chip_mantis': chip_mantis,
                'alert': alerts,
            }
            return render(request, 'design/experiment.html', context)

        elif step.script == 'Moclo':
            print('Moclo: Yes')

        elif step.script == 'Normalization':
            print('Normalization: Yes')

        elif step.script == '':
            run_results = 'Resultado do step sem script'
            step.status_run = True
            step.save()

        return redirect('design:step_view', experiment.id, step.id)


    context = {
        'all_steps': all_steps,
        'step': step,
        'experiment': experiment,
        'form_experiment_update': formExperimentUpdate,
        'form_step_add': formStepAdd,
        'form_step_update': formStepUpdate,
        'run_results': run_results,
        'outfile:': None,
        'worklist': None,
    }

    return render(request, 'design/experiment.html', context)

@login_required()
def step_update(request, experiment_id, step_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    step = get_object_or_404(Step, id=step_id)
    formExperimentUpdate = ExperimentForm(instance=experiment)
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
        if step.input_file_step is not None: step.input_file_step.delete()
        if step.input_file_script is not None: step.input_file_script.delete()
        step.input_plates.all().delete()
        step.output_files.all().delete()
        step.output_plates.all().delete()
        step.delete()

    return redirect('design:experiment_view', experiment.id)


@login_required()
def step_run(request, experiment_id, step_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    step = get_object_or_404(Step, id=step_id)

    if request.method == 'POST':
        formStepUpdate = StepForm(request.POST, request.FILES, instance=step, initial={'status_run':True})
        if formStepUpdate.is_valid():
            formStepUpdate.save()

    return redirect('design:step_view', experiment.id, step.id)
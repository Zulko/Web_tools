import os

from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.functions import Substr, Cast
from django.db.models import IntegerField
from django.conf import settings

from tablib import Dataset

from .models import Plate, Well, Sample, File, Machine, Project
from .forms import SampleForm, PlateForm, WellForm, MachineForm, ProjectForm
from .filters import SampleFilter, PlateFilter
from .resources import SampleResource, PlateResource
from libs.misc import calc, file


@login_required()
def file_sharing(request):
    files = File.objects.all()
    return render(request, 'db/file_sharing.html', {'files': files})


@login_required()
def delete_file(request, file_id):
    if request.method == 'POST':
        file = File.objects.get(id=file_id)
        file.delete()
    return redirect('db:file_sharing')


@login_required()
def upload_file(request, filename):
    upload = request.FILES[filename]
    fs = FileSystemStorage()
    name = fs.save(upload.name, upload)
    url = fs.url(name)
    return upload, fs, name, url


@login_required()
def plate_list(request):
    all_plates = Plate.objects.all()
    plate_filter = PlateFilter(request.GET, queryset=all_plates)
    formPlateAdd = PlateForm()
    formPlateUpdate = PlateForm()

    if 'submit_plate_add' in request.POST:
        formPlateAdd = PlateForm(request.POST, request.FILES)
        if formPlateAdd.is_valid():
            new_plate = formPlateAdd.save()
            return redirect('db:plate', new_plate.id)

    elif 'form_plate_update' in request.POST:
        formPlateUpdate = PlateForm(request.POST, request.FILES)
        if formPlateUpdate.is_valid():
            new_plate = formPlateUpdate.save()
            return redirect('db:plate', new_plate.id)

    context = {
        'form_plate_add': formPlateAdd,
        'form_plate_update': formPlateUpdate,
        "all_plates": all_plates,
        'filter': plate_filter
    }

    return render(request, 'db/index.html', context)


def plate_layout(plate_id, all_wells):
    plate = get_object_or_404(Plate, id=plate_id)
    well_list = Plate.create_layout(plate)
    layout_fill = []
    for row in well_list:
        row_list = []
        for col in row:
            found = False
            for well in all_wells:
                if col == well.name:
                    row_list.append([col, plate_id, well.id])
                    found = True
            if found is False:
                row_list.append([col, "", ""])
        layout_fill.append(row_list)
    colnames, rownames = Plate.create_headnames(plate)
    layout = zip(rownames, layout_fill)
    return layout, colnames, plate


@login_required()
def plate_view(request, plate_id):
    all_plates = Plate.objects.all()
    plate = get_object_or_404(Plate, id=plate_id)
    plate_filter = PlateFilter(request.GET, queryset=all_plates)
    formPlateAdd = PlateForm()
    formPlateUpdate = PlateForm(instance=plate)
    formWellAdd = WellForm(initial={'plate': plate.id})

    if 'submit_plate_add' in request.POST:
        formPlateAdd = PlateForm(request.POST, request.FILES)
        if formPlateAdd.is_valid():
            new_plate = formPlateAdd.save()
            return redirect('db:plate', new_plate.id)

    elif 'submit_plate_update' in request.POST:
        formPlateUpdate = PlateForm(request.POST, request.FILES, instance=plate)
        if formPlateUpdate.is_valid():
            if plate.active is False:
                wells = Well.objects.filter(plate_id=plate.id)
                for well in wells:
                    well.active = False
                    well.save()
            update_plate = formPlateUpdate.save()
            return redirect('db:plate', update_plate.id)

    elif 'upload_file_plate' in request.POST:
        plate_resources = PlateResource()
        dataset = Dataset()
        new_plate = request.FILES['upload_file_plate']
        imported_data = dataset.load(new_plate.read().decode('utf-8'), format='csv')
        print(imported_data)
        result = plate_resources.import_data(imported_data, dry_run=True, raise_errors=True,
                                             collect_failed_rows=True)
        if not result.has_errors():
            plate_resources.import_data(imported_data, dry_run=False)
        else:
            print(result.invalid_rows)
        return redirect('db:plate', plate.id)

    elif 'submit_add_well' in request.POST:
        formWellAdd = WellForm(request.POST, request.FILES, initial={'plate': plate.id})
        if formWellAdd.is_valid():
            new_well = formWellAdd.save()
            well = get_object_or_404(Well, id=new_well.id)
            return redirect('db:well', plate.id, well.id)

    try:
        all_wells = Well.objects.filter(plate_id=plate_id)
        layout, colnames, plate = plate_layout(plate_id, all_wells)

    except Plate.DoesNotExist:
        raise Http404("Plate does not exist")

    context = {
        'form_plate_add': formPlateAdd,
        'form_plate_update': formPlateUpdate,
        'form_add_well': formWellAdd,
        "all_plates": all_plates,
        'plate': plate,
        'wells': all_wells,
        'layout': layout,
        'colnames': colnames,
        'filter': plate_filter
    }
    return render(request, 'db/plate_view.html', context)


@login_required()
def plate_export(request, plate_id):
    plate_resource = PlateResource()
    plate_filter = Plate.objects.get(id=plate_id)

    try:
        all_wells = Well.objects.filter(plate_id=plate_id).annotate(letter=Substr('name', 1, 1)).annotate(digits=Substr('name', 2)).annotate(number=Cast('digits', IntegerField())).order_by('letter', 'number')
        dataset = plate_resource.export(all_wells)
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(plate_filter)
        return response
    except:
        return None


@login_required()
def plate_print(request, plate_id):
    plate_filter = Plate.objects.get(id=plate_id)
    data_pdf = []
    filename = plate_filter.name + '.pdf'
    filepath = os.path.join(settings.MEDIA_ROOT, "docs", filename)

    for j in range(0, plate_filter.num_rows):
        line = []
        for i in range(0, plate_filter.num_cols):
            try:
                well = Well.objects.get(plate_id=plate_id, name=calc.coordinates_to_wellname(coords=[j, i]))
            except:
                well = None
            if well is not None:
                sample_well = Well.objects.filter(plate_id=plate_id,
                                                  name=calc.coordinates_to_wellname(coords=[j, i])).values_list(
                    'samples__alias', flat=True).get(pk=well.id)
                if sample_well is not None:
                    sample_well = file.smart_split(sample_well, 6, 9)
                    line.append(sample_well)
            else:
                line.append(str(calc.coordinates_to_wellname(coords=[j, i])))
        data_pdf.append(line)

    pdffile = file.create_pdf(filepath, data_pdf, plate_filter.num_rows, plate_filter.num_cols)

    response = FileResponse(open(filepath, 'rb'), content_type='application/pdf')
    return response


@login_required()
def plate_delete(request, plate_id):
    if request.method == 'POST':
        plate = Plate.objects.get(id=plate_id)
        plate.delete()
    return redirect('db:index')


@login_required()
def plate_add(request):
    if 'submit_plate_add' in request.POST:
        formPlate = PlateForm(request.POST, request.FILES)
        if formPlate.is_valid():
            new_plate = formPlate.save()
            return redirect('db:plate', new_plate.id)
    else:
        formPlate = PlateForm()

    context = {
        'form_plate_add': formPlate,
    }
    return render(request, 'db/plate_view.html', context)


@login_required()
def plate_add_file(request):
    if 'upload_file_plate' in request.POST:
        plate_resources = PlateResource()
        dataset = Dataset()
        new_plate = request.FILES['upload_file_plate']
        imported_data = dataset.load(new_plate.read().decode('utf-8'), format='csv')
        result = plate_resources.import_data(imported_data, dry_run=True, raise_errors=True, collect_failed_rows=True)
        if not result.has_errors():
            plate_resources.import_data(imported_data, dry_run=False)
        else:
            print(result.invalid_rows)
        return redirect('db:index')


@login_required()
def plate_update(request, plate_id):
    plate = get_object_or_404(Plate, id=plate_id)
    if 'submit_plate_update' in request.POST:
        formPlate = PlateForm(instance=plate)
        if formPlate.is_valid():
            if plate.active is False:
                wells = Well.objects.filter(plate_id=plate.id)
                for well in wells:
                    well.active = False
                    well.save()
            new_plate = formPlate.save()
            return redirect('db:plate', new_plate.id)
    else:
        formPlate = PlateForm(instance=plate)

    context = {
        'form_plate_update': formPlate,
    }
    return render(request, 'db/plate_view.html', context)


@login_required()
def well(request, plate_id, well_id):
    all_plates = Plate.objects.all()
    plate_filter = PlateFilter(request.GET, queryset=all_plates)
    all_wells = Well.objects.filter(plate_id=plate_id)
    well = get_object_or_404(Well, id=well_id)
    plate = get_object_or_404(Plate, id=plate_id)

    formPlateAdd = PlateForm()
    formPlateUpdate = PlateForm(instance=plate)
    formWellAdd = WellForm(initial={'plate': plate.id})
    formWellUpdate = WellForm(instance=well)

    layout, colnames, plate = plate_layout(plate_id, all_wells)

    if 'submit_plate_add' in request.POST:
        formPlateAdd = PlateForm(request.POST, request.FILES)
        if formPlateAdd.is_valid():
            new_plate = formPlateAdd.save()
            return redirect('db:plate', new_plate.id)

    elif 'submit_plate_update' in request.POST:
        formPlateUpdate = PlateForm(request.POST, request.FILES, instance=plate)
        if formPlateUpdate.is_valid():
            if plate.active is False:
                wells = Well.objects.filter(plate_id=plate.id)
                for well in wells:
                    well.active = False
                    well.save()
            update_plate = formPlateUpdate.save()
            return redirect('db:plate', update_plate.id)

    elif 'upload_file_plate' in request.POST:
        plate_resources = PlateResource()
        dataset = Dataset()
        new_plate = request.FILES['upload_file_plate']
        imported_data = dataset.load(new_plate.read().decode('utf-8'), format='csv')
        result = plate_resources.import_data(imported_data, dry_run=True, raise_errors=True,
                                             collect_failed_rows=True)
        if not result.has_errors():
            plate_resources.import_data(imported_data, dry_run=False)
        else:
            print(result.invalid_rows)
        return redirect('db:plate', plate.id)

    elif 'submit_add_well' in request.POST:
        formWellAdd = WellForm(request.POST, request.FILES, initial={'plate': plate.id})
        if formWellAdd.is_valid():
            new_well = formWellAdd.save()
            well = get_object_or_404(Well, id=new_well.id)
            return redirect('db:well', plate.id, well.id)

    elif 'submit_update_well' in request.POST:
        formWellUpdate = WellForm(request.POST, request.FILES, instance=well)
        if formWellUpdate.is_valid():
            edit_well = formWellUpdate.save()
            well = get_object_or_404(Well, id=edit_well.id)
            return redirect('db:well', plate.id, well.id)

    context = {
        'form_plate_add': formPlateAdd,
        'form_plate_update': formPlateUpdate,
        'form_update_well': formWellUpdate,
        'form_add_well': formWellAdd,
        "all_plates": all_plates,
        'plate': plate,
        'wells': all_wells,
        'layout': layout,
        'colnames': colnames,
        'well': well,
        'filter': plate_filter
    }

    return render(request, 'db/plate_view.html', context)


@login_required()
def well_add(request, plate_id):
    plate = get_object_or_404(Plate, id=plate_id)
    if 'submit_add_well' in request.POST:
        form = WellForm(request.POST, request.FILES)
        if form.is_valid():
            new_well = form.save()
            well = get_object_or_404(Well, id=new_well.id)
            return redirect('db:well', plate.id, well.id)
        else:
            print(form.errors)
    else:
        form = WellForm()

    return render(request, 'db/plate_view.html', {'form_add_well': form})


@login_required()
def well_update(request, plate_id, well_id):
    well = get_object_or_404(Well, id=well_id)
    plate = get_object_or_404(Plate, id=plate_id)
    form = WellForm(request.POST, request.FILES, instance=well)

    if 'submit_update_well' in request.POST:
        if form.is_valid():
            edit_well = form.save()
            well = get_object_or_404(Well, id=edit_well.id)
            return redirect('db:well', plate.id, well.id)
    else:
        form = WellForm(instance=well)

    return render(request, 'db/plate_view.html', {'form_update_well': form})


@login_required()
def well_delete(request, plate_id, well_id):
    if request.method == 'POST':
        well = Well.objects.get(id=well_id)
        well.delete()
    return redirect('db:plate', plate_id=plate_id)


#TODO: Use the filter configuration to create an output file
@login_required()
def sample_export(request):
    sample_resource = SampleResource()
    # sample_filter = Sample.objects.filter(sample_type='Pr')
    sample_filter = Sample.objects.all()
    dataset = sample_resource.export(sample_filter)
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="samples.csv"'

    return response


@login_required()
def sample_delete(request, sample_id):
    if request.method == 'POST':
        sample = Sample.objects.get(id=sample_id)
        all_wells = Well.objects.filter(samples=sample_id)
        sample.delete()
        all_wells.delete()

    return redirect('db:samples_list')


@login_required()
def samples_list(request):
    all_samples = Sample.objects.all()
    sample_filter = SampleFilter(request.GET, queryset=all_samples)
    formSampleAdd = SampleForm()
    formSampleUpdate = SampleForm()

    if 'submit_add_sample' in request.POST:
        formSampleAdd = SampleForm(request.POST, request.FILES)
        if formSampleAdd.is_valid():
            new_sample = formSampleAdd.save()
            sample = get_object_or_404(Sample, id=new_sample.id)
            return redirect('db:sample', sample.id)

    elif 'submit_update_sample' in request.POST:
        formSampleUpdate = SampleForm(request.POST, request.FILES)
        if formSampleUpdate.is_valid():
            update_sample = formSampleUpdate.save()
            sample = get_object_or_404(Sample, id=update_sample.id)
            return redirect('db:sample', sample.id)

    elif 'submit_file_samples' in request.POST:
        samples_resources = SampleResource()
        dataset = Dataset()
        new_samples = request.FILES['upload_file_samples']
        imported_data = dataset.load(new_samples.read().decode('utf-8'), format='csv')
        result = samples_resources.import_data(imported_data, dry_run=True, raise_errors=True, collect_failed_rows=True)
        if not result.has_errors():
            samples_resources.import_data(imported_data, dry_run=False)
        else:
            print(result.invalid_rows)
        return redirect('db:samples_list')

    context = {
        'form_sample': formSampleAdd,
        'form_sample_update': formSampleUpdate,
        "all_samples": all_samples,
        "filter": sample_filter
    }

    return render(request, 'db/samples_list.html', context)


@login_required()
def sample(request, sample_id):
    all_samples = Sample.objects.all()
    sample_filter = SampleFilter(request.GET, queryset=all_samples)
    sample = Sample.objects.get(id=sample_id)
    all_wells = Well.objects.filter(samples=sample_id)
    formSampleView = SampleForm()
    formSampleUpdate = SampleForm(instance=sample)

    if request.method == 'POST':
        formSampleView = SampleForm(request.POST, request.FILES)
        formSampleUpdate = SampleForm(request.POST, request.FILES, instance=sample)

        if formSampleView.is_valid():
            new_sample = formSampleView.save()
            sample = get_object_or_404(Sample, id=new_sample.id)
            return redirect('db:sample', sample.id)
        elif formSampleUpdate.is_valid():
            update_sample = formSampleUpdate.save()
            sample = get_object_or_404(Sample, id=update_sample.id)
            return redirect('db:sample', sample.id)

        if 'submit_add_sample' in request.POST:
            formSampleAdd = SampleForm(request.POST, request.FILES)
            if formSampleAdd.is_valid():
                new_sample = formSampleAdd.save()
                sample = get_object_or_404(Sample, id=new_sample.id)
                return redirect('db:sample', sample.id)

        elif 'submit_update_sample' in request.POST:
            formSampleUpdate = SampleForm(request.POST, request.FILES)
            if formSampleUpdate.is_valid():
                update_sample = formSampleUpdate.save()
                sample = get_object_or_404(Sample, id=update_sample.id)
                return redirect('db:sample', sample.id)

        elif 'submit_file_samples' in request.POST:
            samples_resources = SampleResource()
            dataset = Dataset()
            new_samples = request.FILES['upload_file_samples']
            imported_data = dataset.load(new_samples.read().decode('utf-8'), format='csv')
            result = samples_resources.import_data(imported_data, dry_run=True, raise_errors=True, collect_failed_rows=True)
            if not result.has_errors():
                samples_resources.import_data(imported_data, dry_run=False)
            else:
                print(result.invalid_rows)
            return redirect('db:samples_list')

    context = {
        'form_sample': formSampleView,
        'form_sample_update': formSampleUpdate,
        "all_samples": all_samples,
        "filter": sample_filter,
        "sample": sample,
        "wells": all_wells
    }
    return render(request, 'db/samples_list.html', context)


@login_required()
def add_sample(request):
    if request.method == 'POST':
        formSample = SampleForm(request.POST, request.FILES)
        if formSample.is_valid():
            new_sample = formSample.save()
            return redirect('db:sample', new_sample.id)
        else:
            samples_resources = SampleResource()
            dataset = Dataset()
            new_samples = request.FILES['upload_file_samples']
            imported_data = dataset.load(new_samples.read().decode('utf-8'), format='csv')
            result = samples_resources.import_data(imported_data, dry_run=True, raise_errors=True, collect_failed_rows=True)

            if not result.has_errors():
                samples_resources.import_data(imported_data, dry_run=False)
            else:
                print(result.invalid_rows)
            return redirect('db:samples_list')
    else:
        formSample = SampleForm()

    return render(request, 'db/samples_list.html', {'form_sample': formSample})


@login_required()
def sample_update(request, sample_id):
    sample = Sample.objects.get(id=sample_id)
    if request.method == 'POST':
        formSampleUpdate = SampleForm(instance=sample)
        if formSampleUpdate.is_valid():
            formSampleUpdate.save()
            return redirect('db:samples_list')

    return render(request, 'db/samples_list.html')


@login_required()
def add_file_sample(request):
    if request.method == 'POST':
        samples_resources = SampleResource()
        dataset = Dataset()
        new_samples = request.FILES['upload_file_samples']
        imported_data = dataset.load(new_samples.read().decode('utf-8'), format='csv')
        result = samples_resources.import_data(imported_data, dry_run=True, raise_errors=True, collect_failed_rows=True)

        if not result.has_errors():
            samples_resources.import_data(imported_data, dry_run=False)
        else:
            print(result.invalid_rows)
        return redirect('db:samples_list')
    else:
        formSample = SampleForm()

    return render(request, 'db/samples_list.html')


@login_required()
def machine_list(request):
    all_machines = Machine.objects.all()
    # plate_filter = PlateFilter(request.GET, queryset=all_plates)
    formMachineAdd = MachineForm()
    formMachineUpdate = MachineForm()

    if 'submit_machine_add' in request.POST:
        formMachineAdd = MachineForm(request.POST, request.FILES)
        if formMachineAdd.is_valid():
            formMachineAdd.save()
            return redirect('db:machine_list')

    elif 'submit_update_machine' in request.POST:
        formMachineUpdate = MachineForm(request.POST, request.FILES)
        if formMachineUpdate.is_valid():
            formMachineUpdate.save()
            return redirect('db:machine_list')

    context = {
        'form_machine_add': formMachineAdd,
        'form_machine_update': formMachineUpdate,
        'all_machines': all_machines,
        # 'filter': plate_filter
    }

    return render(request, 'db/machines.html', context)


@login_required()
def machine(request, machine_id):
    all_machines = Machine.objects.all()
    machine = Machine.objects.get(id=machine_id)
    # plate_filter = PlateFilter(request.GET, queryset=all_plates)
    formMachineAdd = MachineForm()
    formMachineUpdate = MachineForm(instance=machine)

    if 'submit_machine_add' in request.POST:
        formMachineAdd = MachineForm(request.POST, request.FILES)
        if formMachineAdd.is_valid():
            formMachineAdd.save()
            return redirect('db:machine_list')

    elif 'submit_update_machine' in request.POST:
        formMachineUpdate = MachineForm(request.POST, instance=machine)
        if formMachineUpdate.is_valid():
            formMachineUpdate.save()
            return redirect('db:machine_list')

    context = {
        'form_machine_add': formMachineAdd,
        'form_machine_update': formMachineUpdate,
        'all_machines': all_machines,
        'machine': machine,
        # 'filter': plate_filter
    }
    return render(request, 'db/machines.html', context)


@login_required()
def machine_add(request):
    if 'submit_machine_add' in request.POST:
        formMachine = MachineForm(request.POST, request.FILES)
        if formMachine.is_valid():
            formMachine.save()
            return redirect('db:machine_list')
    else:
        formMachine = MachineForm()

    context = {
        'form_machine_add': formMachine,
    }
    return render(request, 'db/machines.html', context)


@login_required()
def machine_update(request, machine_id):
    machine = Machine.objects.get(id=machine_id)
    if 'submit_update_machine' in request.POST:
        formMachineUpdate = MachineForm(request.POST, instance=machine)
        if formMachineUpdate.is_valid():
            formMachineUpdate.save()
            return redirect('db:project_list')
    else:
        formMachineUpdate = MachineForm(instance=machine)

    context = {
        'form_machine_update': formMachineUpdate,
    }
    return render(request, 'db/machines.html', context)


@login_required()
def machine_delete(request, machine_id):
    if request.method == 'POST':
        machine = Machine.objects.get(id=machine_id)
        machine.delete()
    return redirect('db:machine_list')


@login_required()
def project_list(request):
    all_project = Project.objects.all()
    # plate_filter = PlateFilter(request.GET, queryset=all_plates)
    formProjectAdd = ProjectForm()
    formProjectUpdate = ProjectForm()

    if 'submit_project_add' in request.POST:
        formProjectAdd = ProjectForm(request.POST, request.FILES)
        if formProjectAdd.is_valid():
            formProjectAdd.save()
            return redirect('db:project_list')

    elif 'form_project_update' in request.POST:
        formProjectUpdate = ProjectForm(request.POST, request.FILES)
        if formProjectUpdate.is_valid():
            formProjectUpdate.save()
            return redirect('db:project_list')

    context = {
        'form_project_add': formProjectAdd,
        'form_project_update': formProjectUpdate,
        'all_project': all_project,
        # 'filter': plate_filter
    }

    return render(request, 'db/projects.html', context)


@login_required()
def project(request, project_id):
    all_project = Project.objects.all()
    project = Project.objects.get(id=project_id)
    # plate_filter = PlateFilter(request.GET, queryset=all_plates)
    formProjectAdd = ProjectForm(initial={'author': request.user.username})
    formProjectUpdate = ProjectForm(instance=project)

    if 'submit_project_add' in request.POST:
        formProjectAdd = ProjectForm(request.POST, request.FILES)
        if formProjectAdd.is_valid():
            formProjectAdd.save()
            return redirect('db:project_list')

    elif 'submit_update_project' in request.POST:
        formProjectUpdate = ProjectForm(request.POST, instance=project)
        if formProjectUpdate.is_valid():
            formProjectUpdate.save()
            return redirect('db:project_list')

    context = {
        'form_project_add': formProjectAdd,
        'form_project_update': formProjectUpdate,
        'all_project': all_project,
        'project': project,
        # 'filter': plate_filter
    }
    return render(request, 'db/projects.html', context)


@login_required()
def project_add(request):
    if 'submit_project_add' in request.POST:
        formProject = ProjectForm(request.POST, request.FILES, initial={'author': request.user.username})
        if formProject.is_valid():
            formProject.save()
            return redirect('db:project_list')
    else:
        formProject = ProjectForm(initial={'author': request.user.username})

    context = {
        'form_project_add': formProject,
    }
    return render(request, 'db/projects.html', context)


@login_required()
def project_update(request, project_id):
    project = Project.objects.get(id=project_id)

    if 'submit_update_project' in request.POST:
        formProjectUpdate = ProjectForm(request.POST, instance=project)
        if formProjectUpdate.is_valid():
            formProjectUpdate.save()
            return redirect('db:project_list')
    else:
        formProjectUpdate = ProjectForm(instance=project)

    context = {
        'form_project_update': formProjectUpdate,
    }
    return render(request, 'db/projects.html', context)


@login_required()
def project_delete(request, project_id):
    if request.method == 'POST':
        project = Project.objects.get(id=project_id)
        project.delete()
    return redirect('db:project_list')
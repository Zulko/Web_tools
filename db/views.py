from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required

from .models import Plate, Well, Sample, File
from .forms import SampleForm, PlateForm, WellForm
from .filters import SampleFilter, PlateFilter
from .resources import SampleResource, PlateResource

from tablib import Dataset


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
    formWellAdd = WellForm()

    if request.method == 'POST':
        formPlateAdd = PlateForm(request.POST, request.FILES)
        formWellAdd = WellForm(request.POST, request.FILES)
        if formPlateAdd.is_valid():
            new_plate = formPlateAdd.save()
            return redirect('db:plate', new_plate.id)
        elif formWellAdd.is_valid():
            new_well = formWellAdd.save()
            return redirect('db:well', new_well.id, new_well.plate.id)

    context = {
        'form_plate_add': formPlateAdd,
        'form_add_well': formWellAdd,
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
    formWellAdd = WellForm(initial={'plate': plate.id})

    if request.method == 'POST':
        plate = get_object_or_404(Plate, id=plate_id)
        formPlate = PlateForm(request.POST, request.FILES)
        formWell = WellForm(request.POST, request.FILES, initial={'plate': plate.id})
        if formPlate.is_valid():
            new_plate = formPlate.save()
            return redirect('db:plate', new_plate.id)
        elif formWell.is_valid():
            new_well = formWell.save()
            well = get_object_or_404(Well, id=new_well.id, initial={'plate': plate.id})
            return redirect('db:well', plate.id, well.id)
    try:
        all_wells = Well.objects.filter(plate_id=plate_id)
        layout, colnames, plate = plate_layout(plate_id, all_wells)

    except Plate.DoesNotExist:
        raise Http404("Plate does not exist")

    context = {
        'form_plate_add': formPlateAdd,
        'form_add_well': formWellAdd,
        "all_plates": all_plates,
        'plate': plate,
        'wells': all_wells,
        'layout': layout,
        'colnames': colnames,
        'filter': plate_filter
    }
    return render(request, 'db/index.html', context)


@login_required()
def plate_export(request, plate_id):
    plate_resource = PlateResource()
    plate_filter = Plate.objects.filter(id=plate_id)
    try:
        all_wells = Well.objects.filter(plate_id=plate_id)
        dataset = plate_resource.export(all_wells)
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="plate.csv"'
        return response
    except:
        return None


@login_required()
def plate_delete(request, plate_id):
    if request.method == 'POST':
        plate = Plate.objects.get(id=plate_id)
        plate.delete()
    return redirect('db:index')


@login_required()
def plate_add(request):
    if request.method == 'POST':
        formPlate = PlateForm(request.POST, request.FILES)
        if formPlate.is_valid():
            new_plate = formPlate.save()
            return redirect('db:plate', new_plate.id)
    else:
        formPlate = PlateForm()

    context = {
        'form_plate_add': formPlate,
    }
    return render(request, 'db/index.html', context)


@login_required()
def well(request, plate_id, well_id):
    all_plates = Plate.objects.all()
    plate_filter = PlateFilter(request.GET, queryset=all_plates)
    all_wells = Well.objects.filter(plate_id=plate_id)
    well = get_object_or_404(Well, id=well_id)
    plate = get_object_or_404(Plate, id=plate_id)

    formPlateAdd = PlateForm()
    formWellAdd = WellForm(initial={'plate': plate.id})
    formWellUpdate = WellForm(instance=well)

    layout, colnames, plate = plate_layout(plate_id, all_wells)

    if 'form_add_well' in request.POST:
        formWellAdd = WellForm(request.POST, request.FILES, initial={'plate': plate.id})
        if formWellAdd.is_valid():
            new_well = formWellAdd.save()
            well = get_object_or_404(Well, id=new_well.id)
            return redirect('db:well', plate.id, well.id)

    elif 'form_update_well' in request.POST:
        formWellUpdate = WellForm(request.POST, request.FILES, instance=well)
        if formWellUpdate.is_valid():
            edit_well = formWellUpdate.save()
            well = get_object_or_404(Well, id=edit_well.id)
            return redirect('db:well', plate.id, well.id)

    context = {
        'form_plate_add': formPlateAdd,
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

    return render(request, 'db/index.html', context)


@login_required()
def well_add(request, plate_id):
    if request.method == 'POST':
        plate = get_object_or_404(Plate, id=plate_id)
        form = WellForm(request.POST, request.FILES)
        if form.is_valid():
            new_well = form.save()
            well = get_object_or_404(Well, id=new_well.id)
            return redirect('db:well', plate.id, well.id)
        else:
            print(form.errors)
    else:
        form = WellForm()

    return render(request, 'db/index.html', {'form_add_well': form})


@login_required()
def well_update(request, plate_id, well_id):
    well = get_object_or_404(Well, id=well_id)
    plate = get_object_or_404(Plate, id=plate_id)
    form = WellForm(instance=well)

    if request.method == 'POST':
        if form.is_valid():
            edit_well = form.save()
            well = get_object_or_404(Well, id=edit_well.id)
            return redirect('db:well', plate.id, well.id)
    # else:
    #     form = WellForm(instance=well)

    return render(request, 'db/index.html', {'form_update_well': form})


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
    formSampleView = SampleForm()
    formSampleUpdate = SampleForm()

    if request.method == 'POST':
        formSampleView = SampleForm(request.POST or None, request.FILES or None)
        if formSampleView.is_valid():
            new_sample = formSampleView.save()
            sample = get_object_or_404(Sample, id=new_sample.id)
            return redirect('db:sample', sample.id)
        elif formSampleUpdate.is_valid():
            update_sample = formSampleUpdate.save()
            sample = get_object_or_404(Sample, id=update_sample.id)
            return redirect('db:sample', sample.id)


    context = {
        'form_sample': formSampleView,
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



# @login_required()
# def create_sample(request):
#     if request.method == 'POST':
#         formSample = SampleForm(request.POST, request.FILES)
#         formPlate = PlateForm(request.POST, request.FILES)
#         if formSample.is_valid():
#             new_sample = formSample.save()
#             return redirect('db:sample', new_sample.id)
#         elif formPlate.is_valid():
#             new_plate = formPlate.save()
#             return redirect('db:index', new_plate)
#         else:
#             samples_resources = SampleResource()
#             dataset = Dataset()
#             new_samples = request.FILES['upload_file_samples']
#             imported_data = dataset.load(new_samples.read().decode('utf-8'), format='csv')
#             result = samples_resources.import_data(imported_data, dry_run=True, raise_errors=True, collect_failed_rows=True)
#
#             if not result.has_errors():
#                 samples_resources.import_data(imported_data, dry_run=False)
#             else:
#                 print(result.invalid_rows)
#             return redirect('db:samples_list')
#     else:
#         formSample = SampleForm()
#         formPlate = PlateForm()
#
#     return render(request, 'db/samples_list.html', {'form_sample': formSample, 'form_plate': formPlate})



# @login_required()
# def create_samples(request):
#     if request.method == 'POST' and request.FILES['upload_file_samples']:
#         samples_resources = SampleResource()
#         dataset = Dataset()
#
#         new_samples = request.FILES['upload_file_samples']
#         for sample in new_samples:
#             print(sample.name)
#
#         imported_data = dataset.load(new_samples.read())
#
#         result = samples_resources.imported_data(dataset, dry_run=True)
#             if not result.has_errors():
#                 samples_resources.import_data(dataset, dry_run=False)
#             return redirect('db:view_sample')
#     else:
#         form = SampleForm()
#     return render(request, 'db/add_data.html', {
#         'form': form
#     })


# @login_required()
# def search_sample(request):
#     all_samples = Sample.objects.all()
#     sample_filter = SampleFilter(request.GET, queryset=all_samples)
#
#     return render(request, 'db/sample_list.html', {"filter": sample_filter})

# def settings(request):
#     if request.method == "POST":
#         form = SiteForm(request.POST, instance=request.user.site_profile)
#         if form.is_valid():
#             form.save()
#             return redirect('dashboard_home')
#     site_profile = Site.objects.get(user=request.user)
#     form = SiteForm(instance=site_profile)
#     return render(request, "dashboard/settings.html", {'form': form })
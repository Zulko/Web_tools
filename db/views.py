from django.views import generic
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required

from .models import Plate, Well, Sample, File
from .forms import SampleForm
from .filters import SampleFilter, PlateFilter
from .resources import SampleResource, PlateResource

from tablib import Dataset


@login_required()
def plate_list(request):
    all_plates = Plate.objects.all()
    plate_filter = PlateFilter(request.GET, queryset=all_plates)
    return render(request, 'db/index.html', {"all_plates": all_plates, 'filter': plate_filter})


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
            if found == False:
                row_list.append([col, "", ""])
        layout_fill.append(row_list)

    colnames, rownames = Plate.create_headnames(plate)
    layout = zip(rownames, layout_fill)
    return layout, colnames, plate


@login_required()
def plate_view(request, plate_id):
    all_plates = Plate.objects.all()
    plate_filter = PlateFilter(request.GET, queryset=all_plates)

    try:
        all_wells = Well.objects.filter(plate_id=plate_id)
        layout, colnames, plate = plate_layout(plate_id, all_wells)

    except Plate.DoesNotExist:
        raise Http404("Plate does not exist")
    return render(request, 'db/index.html',
                  {"all_plates": all_plates, 'plate': plate, 'wells': all_wells, 'layout': layout, 'colnames': colnames, 'filter': plate_filter})


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
def well(request, plate_id, well_id):
    all_plates = Plate.objects.all()
    plate_filter = PlateFilter(request.GET, queryset=all_plates)
    all_wells = Well.objects.filter(plate_id=plate_id)
    well = get_object_or_404(Well, id=well_id)
    layout, colnames, plate = plate_layout(plate_id, all_wells)
    return render(request, 'db/index.html', {"all_plates": all_plates,'plate': plate, 'wells': all_wells, 'layout': layout, 'colnames':colnames, 'well': well, 'filter': plate_filter})


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


#TODO: Use the filter configuration to create an output file
@login_required()
def export_sample(request):
    sample_resource = SampleResource()
    sample_filter = Sample.objects.filter(sample_type='Pr')
    # queryset = Sample.objects.filter(sample_filter)

    dataset = sample_resource.export(sample_filter)

    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="samples.csv"'

    return response


@login_required()
def sample_list(request):
    all_samples = Sample.objects.all()
    sample_filter = SampleFilter(request.GET, queryset=all_samples)

    return render(request, 'db/sample_list.html', {"all_samples": all_samples, "filter": sample_filter})


@login_required()
def sample(request, sample_id):
    all_samples = Sample.objects.all()
    sample_filter = SampleFilter(request.GET, queryset=all_samples)
    sample = Sample.objects.get(id=sample_id)
    all_wells = Well.objects.filter(samples=sample_id)

    return render(request, 'db/sample_list.html', {"all_samples": all_samples, "filter": sample_filter, "sample": sample, "wells": all_wells})


@login_required()
def create_sample(request):
    if request.method == 'POST':
        form = SampleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('db:view_sample')
        else:
            samples_resources = SampleResource()
            dataset = Dataset()
            new_samples = request.FILES['upload_file_samples']

            # for sample in new_samples:
            #     print(sample.name)
            imported_data = dataset.load(new_samples.read())

            result = samples_resources.import_data(dataset, dry_run=True)
            if not result.has_errors():
                samples_resources.import_data(dataset, dry_run=False)
            return render(request, 'db/sample_list.html')
    else:
        form = SampleForm()
    return render(request, 'db/add_data.html', {
        'form': form
    })


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
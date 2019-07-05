from django.views import generic
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required

from .models import Plate, Well, Sample, File
from .forms import SamplePrimerForm


class IndexView(generic.ListView):
    template_name = 'db/index.html'
    context_object_name = 'all_plates'

    def get_queryset(self):
        return Plate.objects.all()


@login_required(login_url="/accounts/login/")
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


@login_required(login_url="/accounts/login/")
def plate(request, plate_id):
    all_plates = Plate.objects.all()
    try:
        all_wells = Well.objects.filter(plate_id=plate_id)
        layout, colnames, plate = plate_layout(plate_id, all_wells)

    except Plate.DoesNotExist:
        raise Http404("Plate does not exist")
    return render(request, 'db/index.html', {"all_plates": all_plates,'plate': plate, 'wells': all_wells, 'layout': layout, 'colnames':colnames})


@login_required(login_url="/accounts/login/")
def well(request, plate_id, well_id):
    all_plates = Plate.objects.all()
    all_wells = Well.objects.filter(plate_id=plate_id)
    well = get_object_or_404(Well, id=well_id)
    layout, colnames, plate = plate_layout(plate_id, all_wells)
    return render(request, 'db/index.html', {"all_plates": all_plates,'plate': plate, 'wells': all_wells, 'layout': layout, 'colnames':colnames, 'well': well})


@login_required(login_url="/accounts/login/")
def file_sharing(request):
    files = File.objects.all()
    return render(request, 'db/file_sharing.html', {'files': files})


@login_required(login_url="/accounts/login/")
def delete_file(request, file_id):
    if request.method == 'POST':
        file = File.objects.get(id=file_id)
        file.delete()
    return redirect('db:file_sharing')


@login_required(login_url="/accounts/login/")
def sample_list(request):
    all_samples = Sample.objects.all()
    return render(request, 'db/sample_list.html', {"all_samples": all_samples})


@login_required(login_url="/accounts/login/")
def add_data(request):
    return render(request, 'db/add_data.html')


@login_required(login_url="/accounts/login/")
def create_sample(request):
    if request.method == 'POST':
        form = SamplePrimerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('db:view_sample')
    else:
        form = SamplePrimerForm()
    return render(request, 'db/add_data.html', {
        'form': form
    })
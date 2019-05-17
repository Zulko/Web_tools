from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Plate, Well, Sample
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(login_url="/accounts/login/")
def index(request):
    all_plates = Plate.objects.all()
    context = {"all_plates": all_plates,}
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
            if found == False:
                row_list.append([col, "", ""])
        layout_fill.append(row_list)

    colnames, rownames = Plate.create_headnames(plate)
    layout = zip(rownames, layout_fill)

    return layout, colnames, plate


def plate(request, plate_id):
    all_plates = Plate.objects.all()
    try:
        all_wells = Well.objects.filter(plate_id=plate_id)
        layout, colnames, plate = plate_layout(plate_id, all_wells)

    except Plate.DoesNotExist:
        raise Http404("Plate does not exist")
    return render(request, 'db/index.html', {"all_plates": all_plates,'plate': plate, 'wells': all_wells, 'layout': layout, 'colnames':colnames})


def well(request, plate_id, well_id):
    all_plates = Plate.objects.all()
    all_wells = Well.objects.filter(plate_id=plate_id)
    well = get_object_or_404(Well, id=well_id)
    layout, colnames, plate = plate_layout(plate_id, all_wells)

    return render(request, 'db/index.html', {"all_plates": all_plates,'plate': plate, 'wells': all_wells, 'layout': layout, 'colnames':colnames, 'well': well})



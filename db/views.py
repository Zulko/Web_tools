from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Plate, Well, Sample


# Create your views here.

def index(request):
    all_plates = Plate.objects.all()
    context = {"all_plates": all_plates,}
    return render(request, 'db/index.html', context)


def plate_layout(plate_id):
    plate = get_object_or_404(Plate, id=plate_id)
    well_list = Plate.create_layout(plate)
    colnames, rownames = Plate.create_headnames(plate)
    layout = zip(rownames, well_list)
    return layout, colnames, plate


def plate(request, plate_id):
    all_plates = Plate.objects.all()
    try:
        all_wells = Well.objects.filter(plate_id=plate_id)
        layout, colnames, plate = plate_layout(plate_id)
    except Plate.DoesNotExist:
        raise Http404("Plate does not exist")
    return render(request, 'db/index.html', {"all_plates": all_plates,'plate': plate, 'wells': all_wells, 'layout': layout, 'colnames':colnames})


def well(request, plate_id, well_id):
    all_plates = Plate.objects.all()
    all_wells = Well.objects.filter(plate_id=plate_id)

    plate = get_object_or_404(Plate, id=plate_id)
    well = get_object_or_404(Well, id=well_id)

    layout = Plate.create_layout(plate)
    colnames, rownames = Plate.create_headnames(plate)
    mylist = zip(rownames, layout)

    return render(request, 'db/index.html', {"all_plates": all_plates,'plate': plate, 'wells': all_wells, 'layout': mylist, 'colnames':colnames, 'rownames':rownames,'well': well})



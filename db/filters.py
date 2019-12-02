import django_filters
from .models import Plate, Well, Sample, File


class SampleFilter(django_filters.FilterSet):

    class Meta:
        model = Sample
        fields = {
            'name': ['icontains', ],
            'alias': ['icontains', ],
            'author': ['icontains', ],
            'project': ['exact', ],
            'sample_type': ['exact', ],
        }


class PlateFilter(django_filters.FilterSet):

    class Meta:
        model = Plate
        fields = {
            'name': ['icontains', ],
            'barcode': ['exact', ],
            'project': ['exact', ],
            'function': ['exact', ],
        }
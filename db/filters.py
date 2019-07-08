import django_filters
from .models import Plate, Well, Sample, File


class SampleFilter(django_filters.FilterSet):
    # name = django_filters.CharFilter(lookup_expr='icontains')
    # alias = django_filters.CharFilter(lookup_expr='icontains')
    # author = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Sample
        fields = {
            'name': ['icontains', ],
            'alias': ['icontains', ],
            'author': ['icontains', ],
            'sample_type': ['exact', ],
        }
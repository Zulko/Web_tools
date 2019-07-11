from import_export import resources
from .models import Sample, Plate


class SampleResource(resources.ModelResource):
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)

    class Meta:
        model = Sample

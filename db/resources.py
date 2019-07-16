from import_export import resources, fields
from .models import Sample, Plate, Well


class SampleResource(resources.ModelResource):
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)

    class Meta:
        model = Sample


class PlateResource(resources.ModelResource):
    name = fields.Field(attribute='name', column_name='well')

    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)

    #TODO: change samples id for samples name
    class Meta:
        model = Well
        fields = ('name', 'samples', 'volume', 'concentration')
        export_order = ('name', 'samples', 'volume', 'concentration')



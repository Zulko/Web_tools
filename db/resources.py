from import_export import resources, fields
from .models import Sample, Plate, Well


class SampleResource(resources.ModelResource):
    # def for_delete(self, row, instance):
    #     return self.fields['delete'].clean(row)

    class Meta:
        skip_unchanged = True
        report_skipped = False
        model = Sample


class PlateResource(resources.ModelResource):
    name = fields.Field(attribute='name', column_name='well')

    #TODO: change samples id for samples name
    class Meta:
        skip_unchanged = True
        model = Well
        fields = ('name', 'samples', 'volume', 'concentration')
        export_order = ('name', 'samples', 'volume', 'concentration')



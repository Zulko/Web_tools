from import_export import resources, fields, widgets
from .models import Sample, Plate, Well


class SampleResource(resources.ModelResource):
    # def for_delete(self, row, instance):
    #     return self.fields['delete'].clean(row)
    class Meta:
        model = Sample
        skip_unchanged = True
        report_skipped = False


class PlateResource(resources.ModelResource):
    plate = fields.Field(
        column_name='plate',
        attribute='plate',
        widget=widgets.ForeignKeyWidget(Well, field='name')
    )
    samples = fields.Field(
        column_name='samples',
        attribute='samples',
        widget=widgets.ManyToManyWidget(Sample, field='name')
    )

    class Meta:
        model = Well
        skip_unchanged = True
        fields = ('name', 'plate', 'samples', 'volume', 'concentration', 'active', 'status')
        export_order = ('plate', 'name', 'samples', 'volume', 'concentration', 'active', 'status')




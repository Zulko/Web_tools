from import_export import resources, fields, widgets
from .models import Sample, Plate, Well


class SampleResource(resources.ModelResource):
    parent_id = fields.Field(
        column_name='parent_id',
        attribute='parent_id',
        widget=widgets.ForeignKeyWidget(Sample, 'name')
    )
    sub_sample_id = fields.Field(
        column_name='sub_sample_id',
        attribute='sub_sample_id',
        widget=widgets.ManyToManyWidget(Sample, field='name')
    )

    class Meta:
        model = Sample
        exclude = ('id', 'created_at', 'updated_at')
        import_id_fields = ['name']
        skip_unchanged = True
        report_skipped = False
        fields = ('name', 'alias', 'sample_type', 'description', 'project', 'author', 'sequence',
                  'length', 'genbank', 'source_reference', 'comments', 'parent_id',
                  'organism', 'genus_specie', 'marker', 'application', 'strategy', 'seq_verified', 'origin_rep',
                  'cloning_system', 'strand', 'order_number', 'part_type', 'moclo_type', 'sub_sample_id', 'end',
                  'direction', 'tm')


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




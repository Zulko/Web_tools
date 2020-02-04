from import_export import resources, fields, widgets
from db.models import Sample, Plate, Well, Project


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
    project = fields.Field(
        column_name='project',
        attribute='project',
        widget=widgets.ManyToManyWidget(Project, field='name')
    )

    class Meta:
        model = Sample
        exclude = ('id', 'created_at', 'updated_at')
        import_id_fields = ['name']
        skip_unchanged = False
        report_skipped = False
        fields = ('name', 'alias', 'sample_type', 'description', 'project', 'author', 'sequence',
                  'length', 'genbank', 'source_reference', 'comments', 'parent_id',
                  'organism', 'genus_specie', 'marker', 'application', 'strategy', 'seq_verified', 'origin_rep',
                  'cloning_system', 'strand', 'order_number', 'part_type', 'moclo_type', 'sub_sample_id', 'primer_id', 'end',
                  'direction', 'tm')


class PlateResource(resources.ModelResource):

    name = fields.Field(
        column_name='well',
        attribute='name',
    )
    plate = fields.Field(
        column_name='plate',
        attribute='plate',
        widget=widgets.ForeignKeyWidget(Plate, field='name')
    )
    samples = fields.Field(
        column_name='samples',
        attribute='samples',
        widget=widgets.ManyToManyWidget(Sample, field='name')
    )
    alias = fields.Field(
        column_name='alias',
        attribute='samples',
        widget=widgets.ManyToManyWidget(Sample, field='alias')
    )
    project = fields.Field(
        column_name='project',
        attribute='plate__project',
        widget=widgets.ManyToManyWidget(Plate, field='name')
    )
    barcode = fields.Field(
        column_name='barcode',
        attribute='plate',
        widget=widgets.ForeignKeyWidget(Plate, field='barcode')
    )
    function = fields.Field(
        column_name='function',
        attribute='plate',
        widget=widgets.ForeignKeyWidget(Plate, field='function')
    )
    plate_content = fields.Field(
        column_name='contents',
        attribute='plate',
        widget=widgets.ForeignKeyWidget(Plate, field='contents')
    )
    plate_medium = fields.Field(
        column_name='medium',
        attribute='plate',
        widget=widgets.ForeignKeyWidget(Plate, field='medium')
    )
    plate_wells = fields.Field(
        column_name='wells',
        attribute='plate',
        widget=widgets.ForeignKeyWidget(Plate, field='num_well')
    )
    plate_type = fields.Field(
        column_name='type',
        attribute='plate',
        widget=widgets.ForeignKeyWidget(Plate, field='type')
    )
    well_description = fields.Field(
        column_name='description',
        attribute='description',
    )
    well_comments = fields.Field(
        column_name='comments',
        attribute='comments',
    )
    well_quadrant = fields.Field(
        column_name='quadrant',
        attribute='quadrant'
    )

    # def import_row(self, row, instance_loader, **kwargs):
    #     # overriding import_row to ignore errors and skip rows that fail to import
    #     # without failing the entire import
    #     import_result = super(PlateResource, self).import_row(row, instance_loader, **kwargs)
    #     if import_result.import_type == RowResult.IMPORT_TYPE_ERROR:
    #         # Copy the values to display in the preview report
    #         import_result.diff = [row[val] for val in row]
    #         # Add a column with the error message
    #         import_result.diff.append('Errors: {}'.format([err.error for err in import_result.errors]))
    #         # clear errors and mark the record to skip
    #         import_result.errors = []
    #         import_result.import_type = RowResult.IMPORT_TYPE_SKIP
    #
    #     return import_result

    class Meta:
        exclude = ('id',)
        import_id_fields = ['name', 'plate']
        # skip_unchanged = True
        # report_skipped = True
        # raise_errors = False
        model = Well

        fields = ('name', 'plate', 'samples', 'alias', 'volume', 'concentration', 'active', 'status')
        # fields = ('name', 'plate', 'samples', 'alias', 'project', 'barcode', 'function', 'plate_content',
        #           'plate_medium', 'plate_wells', 'plate_type', 'well_description', 'well_comments', 'well_quadrant',
        #           'volume', 'concentration', 'active', 'status')

        # export_order = (
        #     'project',
        #     'barcode',
        #     'plate',
        #     'name',
        #     'samples',
        #     'alias',
        #     'volume',
        #     'concentration',
        #     'active',
        #     'status',
        #     'plate_type',
        #     'plate_content',
        #     'plate_medium',
        #     'plate_wells',
        #     'plate_function',
        #     'well_description',
        #     'well_comments',
        #     'well_quadrant',)

        def get_queryset(self):
            return self.model.objects.all().order_by('name')
        # return self._meta.model.objects.order_by('name')





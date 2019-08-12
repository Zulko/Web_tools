from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Plate, Sample, Well, File


# Register your models here.

# admin.site.register(Plate)
# admin.site.register(Sample)
# admin.site.register(Well)
# admin.site.register(File)

@admin.register(Well)
class WellAdmin(ImportExportModelAdmin):
    pass


@admin.register(Plate)
class PlateAdmin(ImportExportModelAdmin):
    pass


@admin.register(Sample)
class SampleAdmin(ImportExportModelAdmin):
    list_display = ['name', 'alias', 'sample_type', 'description', 'project', 'author', 'sequence',
                  'length', 'genbank', 'source_reference', 'comments', 'parent_id',
                  'organism', 'genus_specie', 'marker', 'application', 'strategy', 'seq_verified', 'origin_rep',
                  'cloning_system', 'strand', 'order_number', 'part_type', 'moclo_type', 'subsample_names', 'end',
                  'direction', 'tm']
    pass


@admin.register(File)
class FileAdmin(ImportExportModelAdmin):
    pass

from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Plate, Sample, Well, File, Machine, Project


# Register your models here.

# admin.site.register(Plate)
# admin.site.register(Sample)
# admin.site.register(Well)
# admin.site.register(File)

@admin.register(Well)
class WellAdmin(ImportExportModelAdmin):
    list_display = ['name','plate']
    ordering = ['plate','name']
    pass


@admin.register(Plate)
class PlateAdmin(ImportExportModelAdmin):
    list_display = [
            'name', 'barcode', 'type', 'contents', 'location', 'num_cols', 'num_rows', 'num_well', 'function',
            'active', 'status']
    pass


@admin.register(Sample)
class SampleAdmin(ImportExportModelAdmin):
    list_display = ['name', 'alias', 'sample_type', 'description']
    pass


@admin.register(File)
class FileAdmin(ImportExportModelAdmin):
    pass


@admin.register(Machine)
class MachineAdmin(ImportExportModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    pass
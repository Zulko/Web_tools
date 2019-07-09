from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Plate, Sample, Well, File


# Register your models here.

admin.site.register(Plate)
# admin.site.register(Sample)
admin.site.register(Well)
admin.site.register(File)


@admin.register(Sample)
class SampleAdmin(ImportExportModelAdmin):
    pass
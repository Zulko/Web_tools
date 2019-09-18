from import_export.admin import ImportExportModelAdmin
from django.contrib import admin

from .models import Experiment, Step

# Register your models here.


@admin.register(Experiment)
class ExperimentAdmin(ImportExportModelAdmin):
    pass


@admin.register(Step)
class StepAdmin(ImportExportModelAdmin):
    pass
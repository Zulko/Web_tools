from import_export.admin import ImportExportModelAdmin
from django.contrib import admin

from .models import Experiment, Step

# Register your models here.


@admin.register(Experiment)
class ExperimentAdmin(ImportExportModelAdmin):
    list_display = ['name', 'project', 'author', 'input_file', 'status', 'created_at']
    pass


@admin.register(Step)
class StepAdmin(ImportExportModelAdmin):
    list_display = ['name', 'experiment', 'description', 'script', 'input_file_step', 'input_file_script', 'status_run',
                    'created_at']
    pass
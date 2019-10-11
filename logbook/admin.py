from import_export.admin import ImportExportModelAdmin
from django.contrib import admin

from .models import LogBook

# Register your models here.


@admin.register(LogBook)
class LogBookAdmin(ImportExportModelAdmin):
    pass
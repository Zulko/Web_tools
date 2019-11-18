from import_export.admin import ImportExportModelAdmin
from django.contrib import admin

from .models import LogBook

# Register your models here.

# admin.site.register(LogBook)
@admin.register(LogBook)
class LogBookAdmin(ImportExportModelAdmin):
    list_display = ['id', 'machine', 'user', 'created_at', 'comments']
    ordering = ['machine', 'created_at']
    pass
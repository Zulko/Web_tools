from django.contrib import admin
from .models import Plate, Sample, Well, File


# Register your models here.

admin.site.register(Plate)
admin.site.register(Sample)
admin.site.register(Well)
admin.site.register(File)

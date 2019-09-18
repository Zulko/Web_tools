from django.db import models
from db.models import File, Sample, Plate, Well

# Create your models here.


class Step(models.Model):
    SCRIPTS = (
        ('Moclo', 'Moclo'),
        ('Normalization', 'Normalization'),
        ('Spotting', 'Spotting'),
    )

    INSTRUMENTS = (
        ('Echo', 'Echo'),
        ('Mantis', 'Mantis'),
        ('Biomek', 'Biomek'),
        ('QIAquick96', 'QIAquick96'),
        ('Qpix', 'Qpix'),
        ('Thermal Cycler', 'Thermal Cycler'),
        ('Fragment Analyzer', 'Fragment Analyzer'),
    )

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    script = models.CharField(max_length=30, choices=SCRIPTS, blank=True)
    instrument = models.CharField(max_length=30, blank=True)
    input_file = models.FileField(upload_to='design/', max_length=10000, blank=True)
    input = models.ManyToManyField(Plate, blank=True, related_name='input_plates')
    # Create new plates by the script
    output = models.ManyToManyField(Plate, blank=True, related_name='output_plates')
    # relationship = table with relatioship between plate/well source and destination including samples, volume and concentration.

    def __str__(self):
        return self.name


class Experiment(models.Model):
    PROJECT = (
        ('GF', 'GF_general'),
        ('SA', 'Sanguinarine'),
        ('MK', 'MoClo kit'),
        ('YK', 'Yeast CRISPR kit'),
    )
    STATUS = (
        ('On going', 'On going'),
        ('Completed', 'Completed'),
        ('Aborted', 'Aborted'),
        ('On hold', 'On hold'),
    )

    name = models.CharField(max_length=100)
    project = models.CharField(max_length=100, blank=True)
    author = models.CharField(max_length=30)
    workflow = models.ManyToManyField(Step, blank=True)
    status = models.CharField(default='On going', max_length=30, choices=STATUS, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.name
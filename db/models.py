# Create sql to do migration -> python manage.py makemigrations db
# Then, make the migrate -> python manage.py migrate
from django.contrib.auth.models import User

import libs.misc.calc as calc

from django.db import models
from django.urls import reverse


class Plate(models.Model):
    STATUS = (
        ('G', 'On going'),
        ('C', 'Completed'),
        ('A', 'Aborted'),
        ('H', 'On hold'),
    )

    def get_barcode():
        num = Plate.objects.count()
        if num is None:
            num = 1
            return '{0:07}'.format(num)
        else:
            num +=1
            return '{0:07}'.format(num)

    name = models.CharField(max_length=50, unique=True)
    barcode = models.IntegerField(unique=True, default=get_barcode)
    num_cols = models.IntegerField()
    num_rows = models.IntegerField()
    num_well = models.IntegerField()
    active = models.BooleanField(default=True)
    status = models.CharField(max_length=1, choices=STATUS, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        ordering = ('id',)

    def get_absolute_url(self):
        return reverse('db:index', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    def create_layout(self):
        layout = []
        for row in range(0, self.num_rows):
            line = []
            for col in range(0, self.num_cols):
                line.append(calc.coordinates_to_wellname(coords=[row, col]))
            layout.append(line)
        return layout

    def create_headnames(self):
        colnames = []
        rownames = []
        for col in range(1, self.num_cols+1):
            colnames.append(col)
        for row in range(0, self.num_rows):
            rownames.append(calc.number_to_rowname(row))
        return colnames, rownames


class Sample(models.Model):
    # Choices
    SAMPLE_TYPES = (
        ('Primer', 'Pr'),
        ('Plasmid', 'Pd'),
        ('Part', 'Pt'),
        ('Linker', 'Lr'),
        ('Other', 'Ot'),
    )
    END_TYPES = (
        ('R', 'Right'),
        ('L', 'Left'),
    )
    PROJECT = (
        ('GF', 'GF_general'),
        ('SA', 'Sanguinarine'),
    )
    PART_TYPE = (
        ('P', 'Promoter'),
        ('T', 'Terminator'),
        ('CDS', 'CDS'),
        ('CR', 'Connector_Right'),
        ('CL', 'Connector_Left'),
        ('B', 'Backbone'),
        ('CS', 'Counter_Screen'),
        ('Ma', 'Marker'),
        ('Mi', 'Miscellaneous'),
    )

    ORGANISM = (
        ('H', 'Human'),
        ('Y', 'Yeast'),
    )
    DIRECTION = (
        ('F', 'Forward'),
        ('R', 'Reverse'),
    )
    STRAND = (
        ('+', 'Positive'),
        ('-', 'Negative'),
    )

    # Database Fields
    name = models.CharField(max_length=50, unique=True)
    alias = models.CharField(max_length=50)
    sample_type = models.CharField(max_length=50, choices=SAMPLE_TYPES, default=SAMPLE_TYPES[4][0])
    description = models.CharField(max_length=100, blank=True)
    project = models.CharField(max_length=30, choices=PROJECT, blank=True)  # Multi select option
    author = models.CharField(max_length=30, blank=True)
    sequence = models.CharField(max_length=10000, blank=True)
    length = models.IntegerField(blank=True, null=True)
    genbank = models.FileField(upload_to='gb_files/', max_length=10000, blank=True)
    source_reference = models.CharField(max_length=30, blank=True)
    comments = models.CharField(max_length=100, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    parent_id = models.IntegerField(blank=True, null=True)  # ID of a sample that was used to originated other
    organism = models.CharField(max_length=1, choices=ORGANISM, blank=True)
    genus_specie = models.CharField(max_length=50, blank=True)
    marker = models.CharField(max_length=50, blank=True)
    application = models.CharField(max_length=50, blank=True)
    strategy = models.CharField(max_length=50, blank=True)
    seq_verified = models.FileField(upload_to='seq/', max_length=10000, blank=True)
    origin_rep = models.CharField(max_length=50, blank=True)
    cloning_system = models.CharField(max_length=50, blank=True)
    strand = models.CharField(max_length=1, choices=STRAND, blank=True)
    order_number = models.CharField(max_length=50, blank=True)

    # Part options
    part_type = models.CharField(max_length=3, choices=PART_TYPE, blank=True)
    moclo_type = models.CharField(max_length=5, blank=True)

    # Plasmid or Primer options
    # Plasmid has parts
    # Primer has linkers
    sub_sample_id = models.IntegerField(null=True, blank=True)  # Multi select option

    # Linker options
    end = models.CharField(max_length=1, choices=END_TYPES, blank=True)

    # Primer option
    direction = models.CharField(max_length=1, choices=DIRECTION, blank=True)
    tm = models.IntegerField(null=True, blank=True)

    # Meta Class
    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Well(models.Model):
    STATUS = (
        ('G', 'On going'),
        ('C', 'Completed'),
        ('A', 'Aborted'),
        ('H', 'On hold'),
    )

    name = models.CharField(max_length=5)
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    concentration = models.DecimalField(max_digits=10, decimal_places=2)
    plate = models.ForeignKey(Plate, on_delete=models.CASCADE)
    samples = models.ManyToManyField(Sample)
    active = models.BooleanField(default=True)
    status = models.CharField(max_length=1, choices=STATUS, blank=True)
    # parent_well = models.ForeignKey()

    class Meta:
        ordering = ('name', 'plate',)

    def __str__(self):
        # well_plate = str(self.name) + ' ' + self.plate.name
        return self.name


class File(models.Model):
    name = models.CharField(max_length=100)
    script = models.CharField(max_length=100, blank=True)
    author = models.CharField(max_length=30)
    file = models.FileField(upload_to='docs/', max_length=10000, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)



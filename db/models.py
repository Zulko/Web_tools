# Create sql to do migration -> python manage.py makemigrations db
# Then, make the migrate -> python manage.py migrate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

import libs.misc.calc as calc

from django.db import models
from django.urls import reverse


class Machine(models.Model):
    MACHINE = (
        ('Accuri C6', 'Accuri C6'),
        ('Tecan Sunrise', 'Tecan Sunrise'),
        ('TapeStation 4150', 'TapeStation 4150'),
        ('Echo 550', 'Echo 550'),
        ('QPix 460', 'QPix 460'),
        ('Biomek FX', 'Biomek FX'),
        ('Mantis', 'Mantis'),
        ('QuBit 4', 'QuBit 4'),
        ('Chromium', 'Chromium'),
        ('MultiFlo FX', 'MultiFlo FX'),
        ('Fragment Analyzer', 'Fragment Analyzer'),
        ('ViiA 7', 'ViiA 7'),
        ('inSPIRE', 'inSPIRE'),
        ('FACSMelody', 'FACSMelody'),
        ('QuantStudio 3D', 'QuantStudio 3D'),

    )
    STATUS = (
        ('Working', 'Working'),
        ('Not working', 'Not working'),
    )

    name = models.CharField(max_length=100, choices=MACHINE, default='Accuri')
    author = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS, default='Working')
    comments = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="pics", max_length=10000, blank=True)
    created_at = models.DateField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.name


class Project(models.Model):
    PROJECT = (
        ('GF_General', 'GF_General'),
        ('Sanguinarine', 'Sanguinarine'),
        ('MoClo_Kit', 'MoClo_Kit'),
        ('Yeast_CRISPR_Kit', 'Yeast_CRISPR_Kit'),
        ('Foundry_Kit', 'Foundry_Kit'),
    )

    STATUS = (
        ('Working', 'Working'),
        ('Not working', 'Not working'),
    )

    name = models.CharField(max_length=100, choices=PROJECT, default='GF_General')
    author = models.CharField(max_length=50)
    collaborators = models.CharField(max_length=500)
    status = models.CharField(max_length=50, choices=STATUS, default='Working')
    comments = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="pics", max_length=10000, blank=True)
    created_at = models.DateField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.name


class Plate(models.Model):
    STATUS = (
        ('Working', 'Working'),
        ('Backup', 'Backup'),
    )
    CONTAINER_TYPES = (
        ('Plate', 'Plate'),
        ('Box', 'Box'),
    )
    CONTAINER_FUNCTION = (
        ('Inventory', 'Inventory'),
        ('Process', 'Process'),
    )
    PROJECT = (
        ('GF_General', 'GF_General'),
        ('Sanguinarine', 'Sanguinarine'),
        ('MoClo_Kit', 'MoClo_Kit'),
        ('Yeast_CRISPR_Kit', 'Yeast_CRISPR_Kit'),
        ('Foundry_Kit', 'Foundry_Kit'),
    )
    CONTENTS = (
        ('DNA', 'DNA'),
        ('Cells', 'Cells'),
        ('Reagents', 'Reagents'),
    )
    LOCATION = (
        ('Fridge', 'Fridge'),
        ('Freezer -20C', 'Freezer -20C'),
        ('Freezer -80C', 'Freezer -80C'),
    )

    def get_barcode():
        try:
            num = Plate.objects.latest('id').id
            num += 1
            name = 'GF' + '{0:05}'.format(num)
            return name
        except ObjectDoesNotExist:
            name = 'GF' + '{0:05}'.format(1)
            return name

    def get_name():
        try:
            num = Plate.objects.latest('id').id
            num += 1
            name = 'Plate_' + '{0:07}'.format(num)
            return name
        except ObjectDoesNotExist:
            name = 'Plate_' + '{0:07}'.format(1)
            return name

    name = models.CharField(max_length=50, unique=True, default=get_name)
    type = models.CharField(max_length=50, choices=CONTAINER_TYPES, default=CONTAINER_TYPES[0][0])
    function = models.CharField(max_length=50, choices=CONTAINER_FUNCTION, default=CONTAINER_TYPES[0][0], blank=True)
    barcode = models.CharField(max_length=30, unique=True, default=get_barcode)
    project = models.CharField(max_length=30, choices=PROJECT, blank=True)  # Multi select option
    num_cols = models.IntegerField()
    num_rows = models.IntegerField()
    num_well = models.IntegerField()
    location = models.CharField(max_length=30, choices=LOCATION, default=LOCATION[0][0], blank=True)
    contents = models.CharField(max_length=30, choices=CONTENTS, default=CONTENTS[0][0], blank=True)
    active = models.BooleanField(default=True)
    status = models.CharField(max_length=30, choices=STATUS, blank=True)
    comments = models.TextField(max_length=500, blank=True)
    created_at = models.DateField(auto_now_add=True, editable=False)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        ordering = ('id',)

    def get_absolute_url(self):
        return reverse('db:index', kwargs={'pk': self.pk})

    def get_num_wells(self):
        return self.num_cols * self.num_rows

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
        ('Primer', 'Primer'),
        ('Plasmid', 'Plasmid'),
        ('Part', 'Part'),
        ('Linker', 'Linker'),
        ('Other', 'Other'),
    )
    END_TYPES = (
        ('R', 'Right'),
        ('L', 'Left'),
    )
    PROJECT = (
        ('GF_General', 'GF_General'),
        ('Sanguinarine', 'Sanguinarine'),
        ('MoClo_Kit', 'MoClo_Kit'),
        ('Yeast_CRISPR_Kit', 'Yeast_CRISPR_Kit'),
        ('Foundry_Kit', 'Foundry_Kit'),
    )
    # PART_TYPE = (
    #     ('Promoter', 'Promoter'),
    #     ('Terminator', 'Terminator'),
    #     ('CDS', 'CDS'),
    #     ('Connector_R', 'Connector_R'),
    #     ('Connector_L', 'Connector_L'),
    #     ('Backbone', 'Backbone'),
    #     ('Counter_Screen', 'Counter_Screen'),
    #     ('Marker', 'Marker'),
    #     ('Miscellaneous', 'Miscellaneous'),
    #     ('Complementation_Marker', 'Complementation_Marker'),
    #     ('S. cerevisiae_marker', 'S. cerevisiae_marker'),
    #     ('Homology', 'Homology'),
    #
    # )
    ORGANISM = (
        ('Human', 'Human'),
        ('Yeast', 'Yeast'),
    )
    DIRECTION = (
        ('FWD', 'Forward'),
        ('REV', 'Reverse'),
    )
    STRAND = (
        ('+', 'Positive'),
        ('-', 'Negative'),
    )

    # Database Fields
    name = models.CharField('Name', max_length=50, unique=True)
    alias = models.CharField(max_length=50)
    sample_type = models.CharField(max_length=50, choices=SAMPLE_TYPES, default=SAMPLE_TYPES[4][0])
    description = models.CharField(max_length=500, blank=True)
    project = models.CharField(max_length=30, choices=PROJECT, blank=True)  # Multi select option
    author = models.CharField(max_length=50, blank=True)
    sequence = models.CharField(max_length=10000, blank=True)
    length = models.IntegerField(blank=True, null=True)
    genbank = models.FileField(upload_to='gb_files/', max_length=10000, blank=True)
    source_reference = models.CharField(max_length=500, blank=True)
    comments = models.CharField(max_length=500, blank=True)
    created_at = models.DateField(default=timezone.now)
    updated_at = models.DateField(auto_now=True)
    parent_id = models.ForeignKey('Sample', null=True, blank=True, on_delete=models.SET_NULL)
    organism = models.CharField(max_length=50, choices=ORGANISM, blank=True)
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
    part_type = models.CharField(max_length=50, blank=True)
    moclo_type = models.CharField(max_length=30, blank=True)

    # Plasmid or Primer options
    # Plasmid has parts
    # Primer has linkers
    sub_sample_id = models.ManyToManyField('Sample', blank=True, related_name='subsample', unique=False)  # Multi select option
    primer_id = models.ManyToManyField('Sample', blank=True, related_name='primer', unique=False)  # Multi select option

    # Linker options
    end = models.CharField(max_length=1, choices=END_TYPES, blank=True)

    # Primer option
    direction = models.CharField(max_length=3, choices=DIRECTION, blank=True)
    tm = models.IntegerField(null=True, blank=True)

    # Meta Class
    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_name(self):
        ":returns a name for the sample"
        num = Sample.objects.filter(self.sample_type).latest('id').id
        if num is None:
            num = 1
            name = self.sample_type + '{0:07}'.format(1)
            return name
        else:
            num += 1
            name = self.sample_type + '{0:07}'.format(num)
            return name

    def subsample_names(self):
        return '\n'.join([a.name for a in self.sub_sample_id.all()])


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
    parent_well = models.ForeignKey('Well', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name', 'plate',)
        unique_together = ('name', 'plate')

    def __str__(self):
        return self.name

    def sample_names(self):
        return '\n'.join([a.name for a in self.samples.all()])


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



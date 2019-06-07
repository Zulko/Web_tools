# Create sql to do migration -> python manage.py makemigrations db
# Then, make the migrate -> python manage.py migrate
from django.contrib.auth.models import User

import libs.misc.calc as calc

from django.db import models
from django.urls import reverse


class Plate(models.Model):
    name = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, unique=True)
    num_cols = models.IntegerField()
    num_rows = models.IntegerField()
    num_well = models.IntegerField()

    class Meta:
        ordering = ('id',)

    def get_absolute_url(self):
        return reverse('db:index',kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    def create_layout(self):
        layout = []
        for row in range(0, self.num_rows):
            line = []
            for col in range(0, self.num_cols):
                line.append(calc.coordinates_to_wellname(coords=[row,col]))
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
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=50)
    project = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_created=True)
    type = models.IntegerField()
    length = models.IntegerField()
    sequence = models.CharField(max_length=10000, blank=True)
    specie = models.CharField(max_length=30)
    parent = models.CharField(max_length=30)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Well(models.Model):
    name = models.CharField(max_length=5)
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    concentration = models.DecimalField(max_digits=10, decimal_places=2)
    plate = models.ForeignKey(Plate, on_delete=models.CASCADE)
    samples = models.ManyToManyField(Sample)
    # parent_well = models.ForeignKey()

    class Meta:
        ordering = ('name', 'plate',)

    def __str__(self):
        well_plate = str(self.name) + ' ' + self.plate.name
        return well_plate


class File(models.Model):
    name = models.CharField(max_length=100)
    script = models.CharField(max_length=100, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='docs/', max_length=10000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)



from django.db import models
import libs.misc.calc as calc


# Create your models here.
# Create sql to do migration -> python manage.py makemigrations db
# Then, make the migrate -> python manage.py migrate


class Plate(models.Model):
    name = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, unique=True)
    num_cols = models.IntegerField()
    num_rows = models.IntegerField()
    num_well = models.IntegerField()

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name

    # def __init__(self, name, barcode, num_cols, num_rows, num_well):
    #     num_well = num_rows*num_cols

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
    type = models.IntegerField()
    length = models.IntegerField()
    sequence = models.CharField(max_length=10000, blank=True)

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

    class Meta:
        ordering = ('name', 'plate',)

    def __str__(self):
        well_plate = str(self.name) + ' ' + self.plate.name
        return well_plate







# Generated by Django 2.1.11 on 2019-10-11 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0017_auto_20191011_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='name',
            field=models.CharField(choices=[('Accuri', 'Accuri'), ('Sunrise', 'Sunrise'), ('TapeStation', 'TapeStation'), ('Echo', 'Echo'), ('QPix', 'QPix'), ('Biomek', 'Biomek'), ('Mantis', 'Mantis'), ('QuBit', 'QuBit'), ('Chromium', 'Chromium'), ('MultiFlow', 'MultiFlow'), ('Fragment Analyzer', 'Fragment Analyzer'), ('ViiA7', 'ViiA7'), ('inSPIRE', 'inSPIRE')], default='Accuri', max_length=100),
        ),
    ]

# Generated by Django 2.1.9 on 2019-08-06 19:28

import db.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('script', models.CharField(blank=True, max_length=100)),
                ('author', models.CharField(max_length=30)),
                ('file', models.FileField(blank=True, max_length=10000, upload_to='docs/')),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=db.models.Plate.get_name, max_length=50, unique=True)),
                ('type', models.CharField(choices=[('Plate', 'Plate'), ('Box', 'Box')], default='Plate', max_length=50)),
                ('barcode', models.IntegerField(default=db.models.Plate.get_barcode, unique=True)),
                ('num_cols', models.IntegerField()),
                ('num_rows', models.IntegerField()),
                ('num_well', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
                ('status', models.CharField(blank=True, choices=[('G', 'On going'), ('C', 'Completed'), ('A', 'Aborted'), ('H', 'On hold')], max_length=1)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
                ('alias', models.CharField(max_length=50)),
                ('sample_type', models.CharField(choices=[('Pr', 'Primer'), ('Pd', 'Plasmid'), ('Pt', 'Part'), ('Lr', 'Linker'), ('Ot', 'Other')], default='Ot', max_length=50)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('project', models.CharField(blank=True, choices=[('GF', 'GF_general'), ('SA', 'Sanguinarine'), ('MK', 'MoClo kit'), ('YK', 'Yeast CRISPR kit')], max_length=30)),
                ('author', models.CharField(blank=True, max_length=50)),
                ('sequence', models.CharField(blank=True, max_length=10000)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('genbank', models.FileField(blank=True, max_length=10000, upload_to='gb_files/')),
                ('source_reference', models.CharField(blank=True, max_length=30)),
                ('comments', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
                ('updated_at', models.DateField(auto_now=True)),
                ('organism', models.CharField(blank=True, choices=[('H', 'Human'), ('Y', 'Yeast')], max_length=1)),
                ('genus_specie', models.CharField(blank=True, max_length=50)),
                ('marker', models.CharField(blank=True, max_length=50)),
                ('application', models.CharField(blank=True, max_length=50)),
                ('strategy', models.CharField(blank=True, max_length=50)),
                ('seq_verified', models.FileField(blank=True, max_length=10000, upload_to='seq/')),
                ('origin_rep', models.CharField(blank=True, max_length=50)),
                ('cloning_system', models.CharField(blank=True, max_length=50)),
                ('strand', models.CharField(blank=True, choices=[('+', 'Positive'), ('-', 'Negative')], max_length=1)),
                ('order_number', models.CharField(blank=True, max_length=50)),
                ('part_type', models.CharField(blank=True, choices=[('P', 'Promoter'), ('T', 'Terminator'), ('CDS', 'CDS'), ('CR', 'Connector_Right'), ('CL', 'Connector_Left'), ('B', 'Backbone'), ('CS', 'Counter_Screen'), ('Ma', 'Marker'), ('Mi', 'Miscellaneous')], max_length=3)),
                ('moclo_type', models.CharField(blank=True, max_length=5)),
                ('sub_sample_id', models.IntegerField(blank=True, null=True)),
                ('end', models.CharField(blank=True, choices=[('R', 'Right'), ('L', 'Left')], max_length=1)),
                ('direction', models.CharField(blank=True, choices=[('F', 'Forward'), ('R', 'Reverse')], max_length=1)),
                ('tm', models.IntegerField(blank=True, null=True)),
                ('parent_id', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='db.Sample')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Well',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=5)),
                ('volume', models.DecimalField(decimal_places=2, max_digits=10)),
                ('concentration', models.DecimalField(decimal_places=2, max_digits=10)),
                ('active', models.BooleanField(default=True)),
                ('status', models.CharField(blank=True, choices=[('G', 'On going'), ('C', 'Completed'), ('A', 'Aborted'), ('H', 'On hold')], max_length=1)),
                ('parent_well', models.ForeignKey(blank=True, default='', null=True, on_delete=False, to='db.Well')),
                ('plate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='db.Plate')),
                ('samples', models.ManyToManyField(to='db.Sample')),
            ],
            options={
                'ordering': ('name', 'plate'),
            },
        ),
    ]

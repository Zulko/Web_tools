# Generated by Django 2.1.11 on 2019-09-19 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design', '0005_auto_20190918_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='input_file',
            field=models.FileField(blank=True, max_length=10000, upload_to='design/'),
        ),
    ]

from django import forms
from django.contrib.auth.models import User
from .models import File, Sample, Plate, Well, Machine, Project


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['name', 'author', 'status', 'comments']


class ProjectForm(forms.ModelForm):
    collaborators = forms.ModelMultipleChoiceField(queryset=User.objects.all())

    class Meta:
        model = Project
        fields = ['name', 'author', 'collaborators', 'status', 'comments']
        widgets = {
            'author': forms.TextInput(attrs={'readonly': 'readonly'}),
        }


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'script', 'author', 'file']


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ['name', 'alias', 'sample_type', 'description', 'project', 'author', 'sequence',
                  'length', 'genbank', 'source_reference', 'comments', 'parent_id',
                  'organism', 'genus_specie', 'marker', 'application', 'strategy', 'seq_verified', 'origin_rep',
                  'cloning_system', 'strand', 'order_number', 'part_type', 'moclo_type', 'sub_sample_id', 'primer_id',
                  'end', 'direction', 'tm']


class PlateForm(forms.ModelForm):
    class Meta:
        model = Plate
        fields = [
            'name', 'barcode', 'type', 'contents', 'location', 'num_cols', 'num_rows', 'num_well', 'function',
            'project', 'active', 'status']


class WellForm(forms.ModelForm):
    class Meta:
        model = Well
        fields = ['name', 'volume', 'concentration', 'plate', 'samples', 'active', 'status']

from django import forms
from .models import File, Sample


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('name', 'script', 'author', 'file')


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ['name', 'alias', 'sample_type', 'description', 'project', 'author', 'sequence',
                  'length', 'genbank', 'source_reference', 'comments', 'parent_id',
                  'organism', 'genus_specie', 'marker', 'application', 'strategy', 'seq_verified', 'origin_rep',
                  'cloning_system', 'strand', 'order_number', 'part_type', 'moclo_type', 'sub_sample_id', 'end',
                  'direction', 'tm']


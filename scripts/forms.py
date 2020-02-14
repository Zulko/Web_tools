from django import forms
from db.models import Plate, Project, Machine


#Design Script Forms
class PrimerForm(forms.Form):
    in_file = forms.FileField(label='Combination file')


class CauldronForm(forms.Form):
    in_file = forms.FileField(label='Combination file')
    zip_file = forms.FileField(label='Zip file')
    enzyme = forms.ChoiceField(
        label='Enzyme',
        choices=(
            ('BsmBI', 'BsmBI'),
            ('BsaI', 'BsaI')
        ),
        initial=['BsmBI', 'BsmBI'],
    )
    topology = forms.ChoiceField(
        label='Topology',
        choices=(
            ('circular', 'Circular'),
            ('linear', 'Linear')
        ),
        initial=['circular', 'Circular'],
    )


#Automate Script Forms
class InputFileForm(forms.Form):
    in_file = forms.FileField(label='Select file')


class PlateFilterForm(forms.Form):
    content = forms.CharField(
        label='Content',
        widget=forms.Select(
            choices=Plate.CONTENTS
        ),
        initial=[Plate.CONTENTS[0][0], Plate.CONTENTS[0][0]],
        # initial=None,
    )
    project = forms.ChoiceField(
        label='Project',
        widget=forms.Select,
        choices=[],
        initial=None,
    )
    plate_ids = forms.MultipleChoiceField(
        label='Plate name',
        widget=forms.SelectMultiple,
        choices=[],
        required=False,
        initial=None,
    )

    def __init__(self, *args, **kwargs):
        super(PlateFilterForm, self).__init__(*args, **kwargs)
        self.fields['project'].choices = [(c.id, c.name) for c in Project.objects.all()]
        self.fields['plate_ids'].choices = [(c.id, c.name) for c in Plate.objects.all()]


class DispenserForm(forms.Form):
    machine = forms.ChoiceField(
        label='Machine',
        widget=forms.Select,
        choices=[],
        required=False,
        initial=['4', 'Echo 550'],
    )
    min_vol = forms.FloatField(
        label='Min volume (nL)',
        max_value=5,
        min_value=1,
        initial=2.5,
    )
    vol_resolution = forms.FloatField(
        label='Volume resolution (nL)',
        max_value=5,
        min_value=1,
        initial=2.5,
    )
    dead_vol = forms.FloatField(
        label='Dead volume (µL)',
        max_value=20,
        min_value=1,
        initial=13,
    )

    def __init__(self, *args, **kwargs):
        super(DispenserForm, self).__init__(*args, **kwargs)
        self.fields['machine'].choices = [(p.pk, p.name) for p in Machine.objects.all()]


class MocloReactionParametersForm(forms.Form):
    part_fmol = forms.IntegerField(
        label='Part (fmol)',
        max_value=40,
        min_value=1,
        initial=40,
    )
    bb_fmol = forms.IntegerField(
        label='Backbone (fmol)',
        max_value=20,
        min_value=1,
        initial=20,
    )
    total_volume = forms.IntegerField(
        label='Total Volume (µL)',
        max_value=20,
        min_value=1,
        initial=10,
    )
    buffer_per = forms.IntegerField(
        label='Buffer (%)',
        max_value=20,
        min_value=1,
        initial=10,
    )
    rest_enz_perc = forms.IntegerField(
        label='Restriction Enzyme (%)',
        max_value=20,
        min_value=1,
        initial=10,
    )
    ligase_per = forms.IntegerField(
        label='Ligase Enzyme (%)',
        max_value=20,
        min_value=1,
        initial=10,
    )
    add_water = forms.BooleanField(
        label='Add water in Master Mix',
        required=False,
        initial=False,
    )
    mantis_two_chips = forms.BooleanField(
        label='Use both a low- and high-volume Mantis chip per reagent',
        required=False,
        initial=False,
    )
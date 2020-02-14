from django import forms
from db.models import Plate


class InputFileForm(forms.Form):
    in_file = forms.FileField(label='Select file')


class DotPlateForm(forms.Form):
    plate_name = forms.MultipleChoiceField(
        label='Plate name',
        widget=forms.SelectMultiple,
        choices=[],
    )
    num_dots = forms.IntegerField(
        label='Number of dots',
        max_value=10,
        min_value=1,
        initial=1,
    )
    dot_vol = forms.IntegerField(
        label='Dot volume (µL)',
        max_value=10,
        min_value=1,
        initial=1,
    )

    def __init__(self, *args, **kwargs):
        super(DotPlateForm, self).__init__(*args, **kwargs)
        self.fields['plate_name'].choices = [(c.id, c.name) for c in Plate.objects.all()]


class DestinationPlateForm(forms.Form):
    num_wells = forms.ChoiceField(
        label='Num wells',
        choices=(
            ('96', '96 wells'),
            ('384', '384 wells')
        ),
        initial='96 wells',
    )
    filled_by = forms.ChoiceField(
        label='Filled by',
        choices=(
            ('1', 'row'),
            ('0', 'column'),
        ),
        initial='row',
    )
    remove_outer_wells = forms.BooleanField(
        label='Remove outer wells',
        required=False,
        initial=False,
    )

# class PrimerForm(forms.Form):

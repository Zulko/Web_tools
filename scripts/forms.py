from django import forms
from django.contrib.auth.models import User
from db.models import Plate


class CauldronForm(forms.Form):
    in_file = forms.FileField(label='Combination file')
    zip_file = forms.FileField(label='Zip file')
    enzyme = forms.ChoiceField(
        label='Enzyme',
        choices=(
            ('BsmBI', 'BsmBI'),
            ('BsaI', 'BsaI')
        ),
        initial='BsmBI',
    )
    topology = forms.ChoiceField(
        label='Topology',
        choices=(
            ('circular', 'Circular'),
            ('linear', 'Linear')
        ),
        initial='circular',
    )
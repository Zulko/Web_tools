from django import forms
from django.contrib.auth.models import User
from db.models import Plate


# class MocloForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         super(MocloForm, self).__init__(*args, **kwargs)
#         self.fields['jobs'].widget.attrs["size"] = 20
#
#     jobs = forms.ModelChoiceField(queryset=Job.objects.all().order_by('name'), empty_label=None, )
#     filter = forms.ChoiceField(choices=filters,
#                                widget=forms.RadioSelect(attrs={
#                                    'onchange': "Dajaxice.tdportal.updatefilter(Dajax.process,{'option':this.value})",
#                                    'name': 'combo1', 'id': 'combo1', },
#                                                         renderer=HorizRadioRenderer),

class NameForm(forms.Form):
    in_file = forms.FileField(label='Combination file')
    zip_file = forms.FileField(label='Zip file')
    enzyme = forms.ChoiceField(
        label='Enzyme',
        choices=(
            ('BsmBI', 'BsmBI'),
            ('BsaI', 'BsaI')
        )
    )
    topology = forms.ChoiceField(
        label='Topology',
        choices=(
            ('Circular', 'Circular'),
            ('Linear', 'Linear')
        )
    )
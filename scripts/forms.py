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
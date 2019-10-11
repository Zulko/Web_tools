from django import forms
from .models import LogBook


class LogBookForm(forms.ModelForm):
    class Meta:
        model = LogBook
        time_used = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
        fields = ['user', 'supervisor', 'time_used', 'comments', 'machine']
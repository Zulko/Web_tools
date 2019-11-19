from django import forms
from .models import LogBook


class LogBookForm(forms.ModelForm):
    class Meta:
        model = LogBook
        time_used = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
        fields = ['user', 'supervisor', 'time_used', 'comments', 'machine']


class LogBookUpdateForm(forms.ModelForm):
    class Meta:
        model = LogBook
        time_used = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
        fields = ['user', 'supervisor', 'time_used', 'comments', 'machine']
        widgets = {'user': forms.TextInput(attrs={'readonly': 'readonly'}),
                   'supervisor': forms.TextInput(attrs={'readonly': 'readonly'}),
                   'time_used': forms.TextInput(attrs={'readonly': 'readonly'}),
                   'machine': forms.TextInput(attrs={'readonly': 'readonly'}),
                   }
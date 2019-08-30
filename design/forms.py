from django import forms
from .models import Experiment, Step


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ['name', 'project', 'author', 'workflow']


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['name', 'description', 'input', 'output']
from django import forms
from .models import Experiment, Step
from db.models import Machine


class ExperimentForm(forms.ModelForm):
    # project = forms.MultipleChoiceField(choices=Experiment.PROJECT, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Experiment
        fields = ['name', 'project', 'author', 'status']
        widgets = {'author': forms.TextInput(attrs={'readonly': 'readonly'})}


class StepForm(forms.ModelForm):
    # machine = forms.MultipleChoiceField(queryset=Machine.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    # TO DO: Add a checkbox

    class Meta:
        model = Step
        fields = ['name', 'status_run', 'description', 'script', 'machine', 'experiment', 'input_file_step',]
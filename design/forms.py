from django import forms
from .models import Experiment, Step


class ExperimentForm(forms.ModelForm):
    # project = forms.MultipleChoiceField(choices=Experiment.PROJECT, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Experiment
        fields = ['name', 'project', 'author', 'status']
        widgets = {'author': forms.TextInput(attrs={'readonly': 'readonly'})}


class StepForm(forms.ModelForm):
    instrument = forms.MultipleChoiceField(choices=Step.INSTRUMENTS, widget=forms.CheckboxSelectMultiple)

    def clean_region(self):
        if len(self.cleaned_data['instrument']) > 3:
            raise forms.ValidationError('Select only 3 option.')
        return self.cleaned_data['instrument']

    class Meta:
        model = Step
        fields = ['name', 'status_run', 'description', 'script', 'instrument', 'experiment', 'input_file_step',]
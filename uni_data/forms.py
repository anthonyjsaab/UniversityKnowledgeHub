from datetime import date

from django.forms import ModelForm
import django.forms as forms
from uni_data.models import Previous


class CreatePreviousForm(ModelForm):
    class Meta:
        model = Previous
        fields = ['file', 'course', 'type', 'semester', 'academic_year']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control', 'placeholder': ' '}),
            'type': forms.Select(attrs={'class': 'form-control', 'placeholder': ' '}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'},
                                          choices=[(y, y) for y in range(date.today().year, 1969, -1)]),
        }

    def save(self, commit=True):
        super(CreatePreviousForm, self).save(commit=commit)

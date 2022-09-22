from django.forms import ModelForm, forms
from storage_conn.views import s3_upload_fileobj
from uni_data.models import Previous


class CreatePreviousForm(ModelForm):
    file = forms.FileField()

    class Meta:
        model = Previous
        exclude = ['s3_object_name', 'submitter']

    def save(self, commit=True):
        s3_upload_fileobj(self.cleaned_data["file"], self.instance.s3_object_name)
        super(CreatePreviousForm, self).save(commit=commit)

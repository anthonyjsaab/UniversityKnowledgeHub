import uuid
from django.forms import ModelForm, forms
from storage_conn.views import s3_upload_fileobj
from uni_data.models import Previous


class CreatePreviousForm(ModelForm):
    file = forms.FileField()

    class Meta:
        model = Previous
        exclude = ['s3_object_name']

    def save(self, commit=True):
        s3_object_name = str(uuid.uuid4())
        self.instance.s3_object_name = s3_object_name
        s3_upload_fileobj(self.cleaned_data["file"], s3_object_name)
        super(CreatePreviousForm, self).save(commit=commit)

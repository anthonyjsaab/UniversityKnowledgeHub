from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView
from storage_conn.views import s3_generate_down_url
from uni_data.forms import CreatePreviousForm
from uni_data.models import Previous


class CreatePreviousView(CreateView, SuccessMessageMixin):
    model = Previous
    form_class = CreatePreviousForm
    success_message = "Transaction created successfully"
    template_name = "for.html"


def download_previous(request):
    if request.method == "POST":
        to_download = Previous.objects.filter(s3_object_name=request.POST["uuid"])
        if to_download:
            return HttpResponseRedirect(s3_generate_down_url(to_download[0].s3_object_name, 180))
    else:
        return render(request, 'down.html')

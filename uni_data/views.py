import uuid
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from authentication.models import MyUser
from storage_conn.views import s3_generate_down_url
from uni_data.forms import CreatePreviousForm
from uni_data.models import Previous


@method_decorator(login_required(login_url='sso_login'), name='dispatch')
class CreatePreviousView(CreateView, SuccessMessageMixin):
    model = Previous
    form_class = CreatePreviousForm
    success_message = "Transaction created successfully"
    template_name = "for.html"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        s3_object_name = str(uuid.uuid4())
        form.instance.file.name = s3_object_name
        form.instance.submitter = self.request.user
        u = self.request.user
        u.previouses_count += 1
        u.save()
        return super().form_valid(form)


@login_required
def download_previous(request):
    if request.method == "POST":
        to_download = Previous.objects.filter(file=request.POST["uuid"])
        if to_download:
            return HttpResponseRedirect(s3_generate_down_url(to_download[0].file.name, 8))
        else:
            return HttpResponse("Huh")
    else:
        return render(request, 'down.html')


def home(request):
    latest_prevs = list(Previous.objects.order_by('id'))
    if len(latest_prevs) > 5:
        latest_prevs = latest_prevs[-5:][::-1]
    best_users = list(MyUser.objects.order_by('-previouses_count'))
    if len(best_users) > 5:
        best_users = best_users[-5:]
    return render(request, 'uni_data/dashboard.html', {'latest_prevs': latest_prevs, 'best_users': best_users})

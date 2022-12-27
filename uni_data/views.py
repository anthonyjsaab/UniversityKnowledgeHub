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
from uni_data.models import Previous, Course, types, Counter4User, Counter4Course


@method_decorator(login_required(login_url='sso_login'), name='dispatch')
class CreatePreviousView(SuccessMessageMixin, CreateView):
    model = Previous
    form_class = CreatePreviousForm
    success_message = "Previous uploaded and stored successfully"
    template_name = "for.html"

    def get_success_url(self):
        u = self.request.user
        c1, c2 = u.counter4user, self.c.counter4course
        c1.prev_count += 1
        c2.prev_count += 1
        c1.save(), c2.save()
        return reverse_lazy('home')

    def form_valid(self, form):
        s3_object_name = str(uuid.uuid4())
        form.instance.file.name = s3_object_name
        form.instance.submitter = self.request.user
        c = form.instance.course
        self.c = c
        return super().form_valid(form)


@login_required
def download_previous(request):
    if request.GET.get("id", False):
        to_download = Previous.objects.filter(id=request.GET.get("id"))
        if to_download:
            return HttpResponseRedirect(s3_generate_down_url(to_download[0].file.name, 8))
        else:
            return HttpResponse("Huh")
    else:
        return HttpResponse("NOT FOUND")


@login_required
def search_page(request):
    context = {'types': [t[0] for t in types]}
    if request.method == "POST":
        context["search_result"] = True
        context["search_params"] = request.POST
        search_kwargs = {}
        if request.POST.get('course', False):
            search_kwargs["course__letter_code"] = request.POST.get('course')[:4]
            search_kwargs["course__number"] = request.POST.get('course')[4:]
        search_kwargs['semester'] = request.POST.get('semester', None)
        search_kwargs['academic_year'] = request.POST.get('year', None)
        search_kwargs['type'] = request.POST.get('type', None)
        search_kwargs_copy = search_kwargs.copy()
        [search_kwargs.pop(key) for key in search_kwargs_copy if not search_kwargs_copy[key]]
        context["results"] = Previous.objects.filter(**search_kwargs)
    return render(request, 'uni_data/search_page.html', context)


def home(request):
    latest_prevs = list(Previous.objects.order_by('id'))
    if len(latest_prevs) > 5:
        latest_prevs = latest_prevs[-5:]
    latest_prevs = latest_prevs[::-1]
    best_user_counters = Counter4User.objects.order_by("-prev_count")
    if len(best_user_counters) > 5:
        best_user_counters = best_user_counters[:5]
    best_users = [counter.user for counter in best_user_counters]
    best_course_counters = Counter4Course.objects.order_by("-prev_count")
    if len(best_course_counters) > 5:
        best_course_counters = best_course_counters[:5]
    best_courses = [counter.course for counter in best_course_counters]
    return render(request, 'uni_data/dashboard.html',
                  {'latest_prevs': latest_prevs, 'best_users': best_users, 'best_courses': best_courses})

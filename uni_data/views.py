import uuid
from functools import wraps
from urllib.parse import urlparse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, resolve_url
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from UniversityKnowledgeHub import settings
from storage_conn.views import s3_generate_down_url
from uni_data.forms import CreatePreviousForm
from uni_data.models import Previous, types, Counter4User, Counter4Course


def request_passes_test(
        test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME
):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                    not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return _wrapped_view

    return decorator


@method_decorator(login_required(), name='dispatch')
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


@login_required
@request_passes_test(
    lambda request: request.GET.get("id", False) and Previous.objects.filter(id=request.GET.get("id")) and
                    Previous.objects.filter(id=request.GET.get("id"))[0].submitter.id == request.user.id)
def delete_previous(request):
    to_delete = Previous.objects.filter(id=request.GET.get("id"))[0]
    course_counter_to_diminish, user_counter_to_diminish = to_delete.course.counter4course, request.user.counter4user
    to_delete.delete()
    course_counter_to_diminish.prev_count -= 1
    user_counter_to_diminish.prev_count -= 1
    course_counter_to_diminish.save(), user_counter_to_diminish.save()
    return redirect('home')

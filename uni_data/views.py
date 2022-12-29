import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import SUCCESS
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView

from authentication.models import MyUser
from storage_conn.views import s3_generate_down_url
from uni_data.forms import CreatePreviousForm, UpdateProfileForm
from uni_data.models import Previous, types, Counter4User, Counter4Course


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
    if request.GET.get("slug", False):
        to_download = Previous.objects.filter(slug=request.GET.get("slug"))
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
        if not request.POST.get('course', False):
            messages.add_message(request, messages.ERROR, "A course must be selected")
            return redirect('search_page')
        search_kwargs["course__letter_code"] = str(request.POST.get('course')[:4]).upper()
        search_kwargs["course__number"] = str(request.POST.get('course')[4:]).upper()
        search_kwargs['semester'] = request.POST.get('semester', None)
        search_kwargs['academic_year'] = request.POST.get('year', None)
        search_kwargs['type'] = request.POST.get('type', None)
        search_kwargs_copy = search_kwargs.copy()
        [search_kwargs.pop(key) for key in search_kwargs_copy if not search_kwargs_copy[key]]
        context["results"] = Previous.objects.filter(**search_kwargs)
    return render(request, 'uni_data/search_page.html', context)


@login_required
def my_submissions(request):
    context = {'types': [t[0] for t in types]}
    if request.method == "POST":
        context["search_params"] = request.POST
        search_kwargs = {}
        if not request.POST.get('course', False):
            messages.add_message(request, messages.ERROR, "A course must be selected")
            return redirect('search_page')
        search_kwargs["course__letter_code"] = str(request.POST.get('course')[:4]).upper()
        search_kwargs["course__number"] = str(request.POST.get('course')[4:]).upper()
        search_kwargs['semester'] = request.POST.get('semester', None)
        search_kwargs['academic_year'] = request.POST.get('year', None)
        search_kwargs['type'] = request.POST.get('type', None)
        search_kwargs_copy = search_kwargs.copy()
        [search_kwargs.pop(key) for key in search_kwargs_copy if not search_kwargs_copy[key]]
        context["results"] = Previous.objects.filter(**search_kwargs).filter(submitter=request.user)
    else:
        context["results"] = Previous.objects.filter(submitter=request.user)
    return render(request, 'uni_data/my_submissions.html', context)


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
def delete_previous(request):
    current_path_of_user = request.POST.get("current_path", "/")
    if not request.GET.get("slug", False):
        # Bad request
        messages.add_message(request, messages.ERROR,
                             "HTTP400: Bad request, cannot delete the previous because its slug was not sent")
        return HttpResponseRedirect(current_path_of_user)
    to_delete = Previous.objects.filter(slug=request.GET.get("slug"))
    if not to_delete:
        # User trying to delete a non-existent previous
        messages.add_message(request, messages.ERROR,
                             "Cannot delete the previous because it does not exist")
        return HttpResponseRedirect(current_path_of_user)
    to_delete = to_delete[0]
    if not to_delete.submitter.id == request.user.id:
        # Forbidden, User trying to delete another user's previous
        messages.add_message(request, messages.ERROR,
                             "HTTP403: Forbidden, you are not allowed to delete this previous")
        return HttpResponseRedirect(current_path_of_user)
    course_counter_to_diminish, user_counter_to_diminish = to_delete.course.counter4course, request.user.counter4user
    to_delete.file.delete(save=False)  # Deleting the file on the S3 bucket
    to_delete.delete()  # Deleting the DB record
    course_counter_to_diminish.prev_count -= 1
    user_counter_to_diminish.prev_count -= 1
    course_counter_to_diminish.save(), user_counter_to_diminish.save()
    messages.add_message(request, SUCCESS, "Previous deleted successfully")
    return HttpResponseRedirect(current_path_of_user)


@method_decorator(login_required(), name='dispatch')
class UpdateProfileView(SuccessMessageMixin, UpdateView):
    form_class = UpdateProfileForm
    model = MyUser
    success_message = "Profile updated successfully"
    template_name = "profile.html"

    def get_object(self, queryset=None):
        return self.request.user

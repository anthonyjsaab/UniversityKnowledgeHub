import json
import uuid
import requests
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from UniversityKnowledgeHub.settings import AD_CLIENT_ID, AD_CLIENT_SECRET
from authentication.models import MyUser, SSOut


def validate_login(request):
    """
    The user sends us the code returned by Microsoft's  API
    :param request:
    :return:
    """
    if not request.GET.get('code', []):
        return HttpResponse("Login Unsuccessful")
    code, session_state = request.GET.get('code'), request.GET.get('session_state')
    data = {
        'client_id': AD_CLIENT_ID,
        'scope': 'openid',
        'grant_type': 'authorization_code',
        'client_secret': AD_CLIENT_SECRET,
        'code': code,
    }
    response = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data=data)
    if str(response.status_code) != '200':
        return HttpResponse("Something went wrong 1")
    j = json.loads(response.content)
    response = requests.get('https://graph.microsoft.com/v1.0/me',
                            headers={'Authorization': f'Bearer {j.get("access_token")}'})
    if str(response.status_code) != '200':
        return HttpResponse("Something went wrong 2")
    j = json.loads(response.content)
    email = j.get('userPrincipalName')
    try:
        obj, created = MyUser.objects.get_or_create(email=email,
                                                    defaults={'email': email, 'username': str(uuid.uuid4()),
                                                              'password': str(uuid.uuid4()) + str(uuid.uuid4())})
        obj.full_clean()
        login(request, obj)
        session = Session.objects.get(session_key=request.session.session_key)
        SSOut.objects.create(microsoft_sessionid=session_state, django_session=session, user=request.user)
        return render(request, 'authentication/empty.html')
    except ValidationError:
        obj.delete()
        logout(request)
        return HttpResponse("Nope")


def test(request):
    if request.user.is_authenticated:
        return HttpResponse(request.user.email)
    else:
        return HttpResponse("Nah")


def log_me_out(request):
    logout(request)
    return HttpResponse("OKM")


def sso_logout(request):
    if 'sid' not in request.GET.keys() or not request.GET.get('sid'):
        return HttpResponse("Ew")
    maybe = SSOut.objects.filter(microsoft_sessionid=request.GET.get('sid'))
    if maybe:
        for ele in maybe:
            ele.django_session.delete()
    return HttpResponse("OK")


def sso_login(request):
    return HttpResponseRedirect(
        f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={AD_CLIENT_ID}'
        '&response_type=code&response_mode=query&scope=openid%20profile%20email%20offline_access%20User.Read')

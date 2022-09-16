import json
import uuid
from django.contrib.auth import login, logout
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.shortcuts import render
import requests
from UniversityKnowledgeHub.settings import AD_CLIENT_ID, AD_CLIENT_SECRET
from authentication.models import MyUser, SSOut


# Create your views here.
def validate_login(request):
    if not request.GET.get('code', []):
        return HttpResponse("Login unsuccessful")
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
        return HttpResponse("Something went wrong")
    j = json.loads(response.content)
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers={'Authorization': f'Bearer {j.get("access_token")}'})
    if str(response.status_code) != '200':
        return HttpResponse("Something went wrong")
    j = json.loads(response.content)
    email = j.get('mail')
    obj, created = MyUser.objects.get_or_create(email=email, defaults={'email': email, 'username': str(uuid.uuid4())})
    login(request, obj)
    session = Session.objects.get(session_key=request.session.session_key)
    ssout = SSOut.objects.create(microsoft_sessionid=session_state, django_session=session, user=request.user)
    return render(request, 'authentication/empty.html')


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
        return HttpResponse('Bruh')
    maybe = SSOut.objects.get(microsoft_sessionid=request.GET.get('sid'))
    if maybe:
        maybe.django_session.delete()
    return HttpResponse("OK")


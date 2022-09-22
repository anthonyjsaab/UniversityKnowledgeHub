import json
import uuid
import requests
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from UniversityKnowledgeHub.settings import AD_CLIENT_ID, AD_CLIENT_SECRET
from authentication.models import MyUser, SSOut


@user_passes_test(lambda user: not user.is_authenticated)  # Authenticated users don't need to give auth code
def validate_login(request):
    """
    The user sends us the code returned by Microsoft's  API.
    Function starts at Step 5 depicted in image "Auth Using Microsoft's Identity Platform.png"
    Note that tokens of depicted Step 7 are never stored. Used once and discarded.
    :param request: Unauthenticated request (guest)
    :return:
    """
    # Checking Step 5 is properly done
    if not request.GET.get('code', []):
        return HttpResponse("Login Unsuccessful, Error 400")
    # Step 6. 'code' is the auth code from Microsoft, 'session_state' used for Single Sign OUT
    code, session_state = request.GET.get('code'), request.GET.get('session_state')
    data = {
        'client_id': AD_CLIENT_ID,
        'scope': 'openid',
        'grant_type': 'authorization_code',
        'client_secret': AD_CLIENT_SECRET,
        'code': code,
    }
    # Step 7
    response = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data=data)
    if str(response.status_code) != '200':
        return HttpResponse("Something went wrong 1")
    # Tokens are below
    j = json.loads(response.content)
    # Below is not is the image, we are using Microsoft Graph to fetch data of user using access tokens of Step 7
    response = requests.get('https://graph.microsoft.com/v1.0/me',
                            headers={'Authorization': f'Bearer {j.get("access_token")}'})
    if str(response.status_code) != '200':
        return HttpResponse("Something went wrong 2")
    j = json.loads(response.content)
    # Below, we get the true, valid email of the user trying to login from a trusted source: Microsoft
    email = j.get('userPrincipalName')
    # Below is empty set if first-time user logging in, contains 1 MyUser object if returning visitor
    filtered = MyUser.objects.filter(email=email)
    if filtered:
        user = filtered[0]
    else:
        # First time user, creating record in DB
        user = MyUser(email=email, username=str(uuid.uuid4()))
        user.set_unusable_password()
    try:
        # Below raises exception if one of the validators are not happy
        user.full_clean()
        # If user's info compliant, new object is saved and visitor is logged in
        user.save()
        login(request, user)
        # Here we are pairing the Django session created by login() with the session_state from Microsoft
        # in a custom SSOut object. This object is used later for Single Sign OUT
        session = Session.objects.get(session_key=request.session.session_key)
        SSOut.objects.create(microsoft_sessionid=session_state, django_session=session, user=request.user)
        return render(request, 'authentication/empty.html')
    except ValidationError:
        # User's info is not compliant, cleanup and abort
        logout(request)
        return HttpResponse("Nope")


def test(request):
    if request.user.is_authenticated:
        return HttpResponse(request.user.email)
    else:
        return HttpResponse("Nah")


def log_me_out(request):
    """
    Manual logout, contrasting with logout ordered by Microsoft when user logs out from another Microsoft site
    :param request:
    :return:
    """
    logout(request)
    return HttpResponse("OKM")


def sso_logout(request):
    """
    Single Sign OUT designed to be invoked by Microsoft when user signs out from Microsoft's site
    :param request:
    :return:
    """
    print(request.user)
    if 'sid' not in request.GET.keys() or not request.GET.get('sid'):
        return HttpResponse("Ew")
    maybe = SSOut.objects.filter(microsoft_sessionid=request.GET.get('sid'))
    if maybe:
        for ele in maybe:
            ele.django_session.delete()
    return HttpResponse("OK")


@user_passes_test(lambda user: not user.is_authenticated)  # Authenticated users don't need to login
def sso_login(request):
    """
    Steps 1 & 2 depicted in image "Auth Using Microsoft's Identity Platform.png"
    :param request: Unauthenticated request (guest)
    :return:
    """
    return HttpResponseRedirect(
        f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={AD_CLIENT_ID}'
        '&response_type=code&response_mode=query&scope=openid%20profile%20email%20offline_access%20User.Read')

import json
import uuid
import requests
import base64

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
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
    # This id_token contains information about the Microsoft user trying to login to our website, notably their email.
    # Since this token comes from Microsoft directly, we can trust it
    # Below, we are decoding the token from base654 to UTF-8
    id_token = j["id_token"]
    relevant_JWT_part = id_token.split(".")[1]
    decoded_token_bin = base64.b64decode(
        bytes(relevant_JWT_part + "=" * (len(relevant_JWT_part) % 4), encoding="UTF-8"))
    decoded_token = json.loads(decoded_token_bin)
    email = decoded_token["email"]
    # Now that we have decoded the id_token and extracted the email, we see if the user is a new or returning visitor
    # We try to see if the DB has any record of this email
    potentialUser = MyUser.objects.filter(email=email)
    if potentialUser:
        # The user is a returning visitor, we have enough evidence that they do have control over the email
        # We will issue them the tokens, no need to use any other Microsoft endpoint
        user = potentialUser[0]
    else:
        # The user is a new visitor, we need to use the userinfo endpoint to get their given_name and family_name
        # This step is not is the image describing the interaction with Microsoft.
        # We are using Microsoft Graph to fetch data of user using access tokens of Step 7
        # The endpoint used is of type OpenID Connect, got it from:
        # https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration
        response = requests.get('https://graph.microsoft.com/oidc/userinfo',
                                headers={'Authorization': f'Bearer {j.get("access_token")}'})
        if str(response.status_code) != '200':
            return HttpResponse("Something went wrong", status=500)
        j = json.loads(response.content)
        # Below, we get the true, valid email of the user trying to login from a trusted source: Microsoft
        first_name, last_name, email = j.get('given_name'), j.get('family_name'), j.get('email')
        user = MyUser(email=email, username=str(uuid.uuid4()), first_name=first_name, last_name=last_name)
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
        if session_state:
            SSOut.objects.create(microsoft_sessionid=session_state, django_session=session, user=request.user)
        return redirect('home')
    except ValidationError:
        # User's info is not compliant, cleanup and abort
        logout(request)
        return HttpResponse("Failed", status=400)


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
    host = request.get_host()
    if "localhost:" not in host and "127.0.0.1:" not in host:
        return redirect(  # Also need to log out from the Microsoft Identity platform
            "https://login.microsoftonline.com/common/oauth2/v2.0/logout"
            f"?post_logout_redirect_uri=https://{host}{reverse_lazy('home')}")
    return redirect('home')


def sso_logout(request):
    """
    Single Sign OUT designed to be invoked by Microsoft when user signs out from Microsoft's site.
    This is necessary. I cannot simply logout(request) because the request ordered by Microsoft would be received
    as coming from AnonymousUser.
    (Refused to display 'https://e93f9cubheicgvfwugvobwqcf.herokuapp.com/' in a frame because it set 'X-Frame-Options'
    to 'deny'.)
    :param request:
    :return:
    """
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
        f'https://login.microsoftonline.com/common/oauth2/authorize?client_id={AD_CLIENT_ID}'
        '&response_type=code&response_mode=query&scope=openid%20profile%20email%20offline_access%20User.Read',
        status=301)

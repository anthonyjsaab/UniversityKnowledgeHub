from django.http import HttpResponseRedirect
from django.urls import path
from UniversityKnowledgeHub.settings import AD_CLIENT_ID
from authentication import views

urlpatterns = [
    path('login/', lambda request: HttpResponseRedirect(
        f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={AD_CLIENT_ID}'
        '&response_type=code&response_mode=query&scope=openid%20profile%20email%20offline_access%20User.Read')),
    path('i_got_code/', views.validate_login),
    path('test/', views.test),
    path('logout/', views.log_me_out),
    path('sso_logout/', views.sso_logout),
    path('up/', views.upload_requirements),
    path('down/', views.download_reqs),
]

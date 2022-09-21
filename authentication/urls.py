from django.http import HttpResponseRedirect
from django.urls import path
from UniversityKnowledgeHub.settings import AD_CLIENT_ID
from authentication import views

urlpatterns = [
    path('sso_login/', views.sso_login),
    path('i_got_code/', views.validate_login),
    path('test/', views.test),
    path('logout/', views.log_me_out),
    path('sso_logout/', views.sso_logout),
    path('up/', views.upload_requirements),
    path('down/', views.download_reqs),
]

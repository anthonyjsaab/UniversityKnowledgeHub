from django.urls import path
from authentication import views


urlpatterns = [
    path('sso_login/', views.sso_login),
    path('i_got_code/', views.validate_login),
    path('test/', views.test),
    path('man_logout/', views.log_me_out),
    path('sso_logout/', views.sso_logout),
]

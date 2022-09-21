from django.urls import path
from uni_data import views


urlpatterns = [
        path('create_prev', views.CreatePreviousView.as_view()),
        path('down_prev', views.download_previous)
]

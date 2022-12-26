from django.urls import path
from uni_data import views


urlpatterns = [
        path('create_prev/', views.CreatePreviousView.as_view(), name='upload'),
        path('down_prev/', views.download_previous, name='download'),
        path('', views.home, name='home'),
        path('search/', views.search_page, name='search_page'),
]

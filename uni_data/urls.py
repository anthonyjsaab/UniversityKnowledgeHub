from django.urls import path
from uni_data import views


urlpatterns = [
        path('create_prev/', views.CreatePreviousView.as_view(), name='upload'),
        path('down_prev/', views.download_previous, name='download'),
        path('delete_prev/', views.delete_previous, name='delete'),
        path('', views.home, name='home'),
        path('search/', views.search_page, name='search_page'),
        path('profile/', views.UpdateProfileView.as_view(), name='profile'),
        path('my_submissions/', views.my_submissions, name='my_submissions'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name = 'home'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate-account'),
]
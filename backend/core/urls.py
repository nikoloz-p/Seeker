from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='home'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
]
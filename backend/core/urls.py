from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name = 'home'),
    path('authorization/', views.auth_view, name='authorization'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate-account'),
    path('account/', views.account_view, name='account'),
    path('logout/', views.logout_view, name='logout'),
]
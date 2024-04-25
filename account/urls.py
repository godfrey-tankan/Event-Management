from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/',views.user_login, name='login'),
    path('edit/', views.edit, name='edit'),
    path('user/', views.request_user_profile, name='request_user_profile'),
  
]
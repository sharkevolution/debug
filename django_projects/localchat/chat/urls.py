# chat/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('rooms/', views.index_view, name='chat-index'),
    path('rooms/<str:room_name>/', views.room_view, name='chat-room'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logged_out.html'), name='logout'),

    path('password-change/',
         auth_views.PasswordChangeView.as_view(template_name='password_change_form.html'),
         name='password_change'),

    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),


]
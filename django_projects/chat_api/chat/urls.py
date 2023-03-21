# chat/urls.py

from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
#     path('', views.index_view, name='chat-index'),
#     path('<str:room_name>/', views.room_view, name='chat-room'),

#     path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
#     path('logout/', auth_views.LogoutView.as_view(template_name='logged_out.html'), name='logout'),

#     path('password-change/',
#          auth_views.PasswordChangeView.as_view(
#              template_name='password_change_form.html'),
#          name='password_change'),

#     path('password-change/done/',
#          auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),


#     # reset password urls
#     path('password-reset/',
#          auth_views.PasswordResetView.as_view(), name='password_reset'),

#     path('password-reset/done/',
#          auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    
#     path('password-reset/<uidb64>/<token>/',
#          auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
#     path('password-reset/complete/',
#          auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('', include('django.contrib.auth.urls')),
    path('chat/', views.index_view, name='chat-index'),
    path('chat/<str:room_name>/', views.room_view, name='chat-room'),
    path('register/', views.register, name='register'),

]

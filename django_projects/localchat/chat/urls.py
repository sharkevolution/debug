# chat/urls.py

from django.urls import path

from . import views

urlpatterns = [
    path('rooms/', views.index_view, name='chat-index'),
    path('login/', views.user_login, name='login'),
    path('rooms/<str:room_name>/', views.room_view, name='chat-room'),
]


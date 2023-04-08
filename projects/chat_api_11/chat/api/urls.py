
from rest_framework_simplejwt import views as jwt_views

from django.urls import path
from . import views

app_name = 'chat'


urlpatterns = [
    path('rooms/', views.RoomsAPIListView.as_view(), name='rooms_api_list'),
    path('rooms/<pk>/', views.RoomsAPIDetailView.as_view(), name='rooms_api_detail'),
]

urlpatterns += [
    # path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('user/create/', views.create_user, name='create_user'),
    # path('users/list/', views.create_user, name='list_users'),
    
    # path('user/delete/', views.create_user, name='create_user'),
    # path('room/create/', views.create_user, name='create_user'),
    # path('room/delete/', views.create_user, name='create_user'),

    # path('room_memberships/add/', views.create_user, name='create_user'),
    # path('room_memberships/remove/', views.create_user, name='create_user'),

    path('sendmessage/', views.send_message_user, name='send_message'),
]

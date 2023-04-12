
from rest_framework_simplejwt import views as jwt_views

from django.urls import path, re_path
from . import views

app_name = 'chat'


urlpatterns = [
    path('rooms/', views.RoomsAPIListView.as_view(), name='rooms_api_list'),
    path('rooms/<pk>/', views.RoomsAPIDetailView.as_view(), name='rooms_api_detail'),
    re_path(r'^roomcontent/(?P<pk>[\w-]+)/$', views.RoomsContentAPIDetailView.as_view(), name='rooms_api_content'),
    
    path('user/create/', views.create_user, name='create_user'),  # Create user and create token
    path('users/', views.UserAPIListView.as_view(), name='users_api'),  # Список пользователей и ИД 
    path('users/<pk>/', views.UserAPIDetailView.as_view(), name='users_api_detail'),  # Детально
    re_path(r'^usersunread/(?P<pk>[\w-]+)/$', views.UserUnreadAPIDetailView.as_view(), name='users_api_unread_text'),
]

urlpatterns += [
    # path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),    
    # path('sendmessage/', views.send_message_user, name='send_message'),
]

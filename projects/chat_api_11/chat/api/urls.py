
from rest_framework_simplejwt import views as jwt_views

from django.urls import path, re_path
from . import views

app_name = 'chat'


urlpatterns = [
    path('rooms/', views.RoomsAPIListView.as_view(), name='rooms_api_list'),
    path('rooms/<pk>/', views.RoomsAPIDetailView.as_view(), name='rooms_api_detail'),
    path('users/', views.UserAPIListView.as_view(), name='users_api'),  # Список пользователей и ИД 
]

urlpatterns += [
    # - одержання списку Thread'ів для будь-якого user'a (у кожному Thread'e має лежати 
    # останнє повідомлення, якщо таке є);
    # Дописать 11.04.2022 
    # path(r'^getuserlist/(?P<id_user>\w+)/(?P<id_room>[\w-]+)/$', views.RoomsAPIDetailView.as_view(), name='user_room_api_detail'),  

]

urlpatterns += [
    # path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('user/create/', views.create_user, name='create_user'),  # Create user and create token
    
    # path('sendmessage/', views.send_message_user, name='send_message'),
]

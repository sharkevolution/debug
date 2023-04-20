
from rest_framework_simplejwt import views as jwt_views

from . import views
from rest_framework import routers
from django.urls import path, re_path, include


app_name = 'chat'

router = routers.DefaultRouter()
router.register('v1/usersend', views.SendMessageUser)
router.register('v1/roomcreate', views.CreateRoomUser)
router.register('v1/users/create', views.Create_user)

urlpatterns = [
 path('', include(router.urls)),
]

urlpatterns += [
    path('v1/rooms/', views.RoomsAPIListView.as_view(), name='rooms_api_list'),
    path('v1/rooms/<int:pk>/', views.RoomsAPIDetailView.as_view(), name='rooms_api_detail'),
    re_path(r'^v1/roomcontent/(?P<pk>[\w-]+)/$', views.RoomsContentAPIDetailView.as_view(), name='rooms_api_content'),
    
    # path('v1/users/create/', views.create_user, name='create_user'),  # Create user and create token
    path('v1/users/', views.UserAPIListView.as_view(), name='users_api'),  # Список пользователей и ИД 
    path('v1/users/<int:pk>/', views.UserAPIDetailView.as_view(), name='users_api_detail'),  # Детально
    re_path(r'^v1/users/unread/(?P<pk>[\w-]+)/$', views.UserUnreadAPIDetailView.as_view(), name='users_api_unread_text'),
]

urlpatterns += [
    # path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),    
]


from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('rooms/', views.SubjectListView.as_view(), name='subject_list'),

    path('rooms/<pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
]


from rest_framework_simplejwt import views as jwt_views

urlpatterns += [
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('user/create/', views.create_user, name='create_user'),
]
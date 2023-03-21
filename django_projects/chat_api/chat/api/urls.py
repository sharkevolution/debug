
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('rooms/', views.SubjectListView.as_view(), name='subject_list'),

    path('rooms/<pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
]

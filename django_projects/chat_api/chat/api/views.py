from rest_framework import generics
from chat.models import Room, Message
from chat.api.serializers import SubjectSerializer
from chat.api.serializers import serializers


class SubjectListView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = SubjectSerializer


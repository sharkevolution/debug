from rest_framework import generics
from chat.models import Room, Message
from chat.api.serializers import SubjectSerializer
from chat.api.serializers import serializers

from rest_framework.permissions import IsAuthenticated

class SubjectListView(generics.ListAPIView):
    queryset = Room.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Room.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = SubjectSerializer


from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions


from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from chat.api.serializers import UserSerializer


@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'data': serializer.data},
            status=status.HTTP_201_CREATED
        )

    return Response(
        {'data': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )
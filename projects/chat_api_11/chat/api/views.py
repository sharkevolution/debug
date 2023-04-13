from rest_framework import generics
from chat.models import Room, Message, User

from django.http.request import QueryDict

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chat.api.serializers import (UserSerializer,
                                    UserListSerializer,
                                    UserDetailSerializer,
                                    UserUnreadDetailSerializer,
                                    RoomSerializer,
                                    RoomDetailSerializer,
                                    RoomContentDetailSerializer,
                                    SendMessagesSerializer, 
                                    MyTokenObtainPairSerializer)

from rest_framework_simplejwt.views import TokenObtainPairView

import logging
logger = logging.getLogger(__name__)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RoomsAPIListPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000


class RoomsAPIListView(generics.ListAPIView):
    """Список комнат
    """
    queryset = Room.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = RoomSerializer
    pagination_class = RoomsAPIListPagination


class RoomsAPIDetailView(generics.RetrieveAPIView):
    """Детальная инфа о комнате и участниках
    """
    queryset = Room.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = RoomDetailSerializer
    pagination_class = RoomsAPIListPagination


class RoomsContentAPIDetailView(generics.RetrieveAPIView):
    """ отримання списку Message для Thread'a;
    """
    queryset = Room.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = RoomContentDetailSerializer
    pagination_class = RoomsAPIListPagination


class UserUnreadAPIDetailView(generics.RetrieveAPIView):
    """ Детально user's unread messages 
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = UserUnreadDetailSerializer
    pagination_class = RoomsAPIListPagination  
 
     
class UserAPIListView(generics.ListAPIView):
    """ Список пользователей id 
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = UserListSerializer
    pagination_class = RoomsAPIListPagination
     
     
class UserAPIDetailView(generics.RetrieveAPIView):
    """ Детально Thread's user 
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = UserDetailSerializer
    pagination_class = RoomsAPIListPagination



@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_user(request):
    ''' 
        Create User and token refresh and access simple JWT
    '''
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(
            {'data': serializer.data},
            status=status.HTTP_201_CREATED
        )

    return Response(
        {'data': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message_user(request):
    """ Отправка сообщения пользователю в комнату Thread
    """
    if isinstance(request.data, QueryDict):
        request.data._mutable = True
        request.data['user'] = request.user.id

    # serializer = SendMessagesSerializer(data=request.data, context={'user_from': request.user})    
    serializer = SendMessagesSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(
            {'data': serializer.data},
            status=status.HTTP_201_CREATED
        )

    return Response(
        {'data': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )

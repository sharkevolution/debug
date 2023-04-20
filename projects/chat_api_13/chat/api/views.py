
from rest_framework_simplejwt.views import TokenObtainPairView

from chat.models import Room, Message, User
from django.http.request import QueryDict

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from chat.api.serializers import (UserSerializer,
                                  UserListSerializer,
                                  UserDetailSerializer,
                                  UserUnreadDetailSerializer,
                                  CreateRoomSerializer,
                                  RoomSerializer,
                                  RoomDetailSerializer,
                                  RoomContentDetailSerializer,
                                  SendMessagesSerializer,
                                  MyTokenObtainPairSerializer)

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


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


class Create_user(viewsets.ReadOnlyModelViewSet):
    ''' 
        Create User and token refresh and access simple JWT
    '''
    queryset = User.objects.all()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def post(self, request, *args, **kwargs):
    
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


class SendMessageUser(viewsets.ReadOnlyModelViewSet):

    queryset = Message.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def post(self, request, *args, **kwargs):
        """ Отправка сообщения пользователю в комнату Thread
        """        
        if isinstance(request.data, QueryDict):
            request.data._mutable = True
            request.data['user'] = request.user.id
            request.data['status_text'] = 'private'
            request.data['is_read'] = 'False'

        serializer = SendMessagesSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # send user message from API
            self.notify_ws_clients(serializer.data)

            return Response({'message sent': True},
                            status=status.HTTP_201_CREATED
                            )

        return Response(
            {'data': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def notify_ws_clients(self, data):
        """
            Send client a new message from API 
        """
        once_text = Message.objects.filter(user=data['user'], recipient=data['recipient'], status_text='private',
                                           room=data['room'], content=data['content']).order_by("created")
        if once_text:
            last_text = once_text.last()
            channel_layer = get_channel_layer()
            
            # send private message to the target
            async_to_sync(channel_layer.group_send)(
                f'inbox_{str(last_text.room.name)}_{str(last_text.recipient)}',
                {
                    'type': 'private_message',
                            'user': str(last_text.user),
                            'message': str(last_text.content),
                            'message_id': last_text.id,
                            'message_is_read': last_text.is_read,
                            'message_created': str(last_text.created.strftime('%Y-%m-%d %H:%M:%S')),
                            'message_status': last_text.is_read,  # Добавляем статус прочитано или нет
                }
            )
            # send private message delivered to the user
            async_to_sync(channel_layer.group_send)(
                f'inbox_{str(last_text.room.name)}_{str(last_text.user)}',
                {
                    'type': 'private_message_delivered',
                    'target': str(last_text.recipient),
                    'message': str(last_text.content),
                    'message_id': last_text.id,
                    'message_is_read': last_text.is_read,
                    'message_created': str(last_text.created.strftime('%Y-%m-%d %H:%M:%S')),
                    'message_status': last_text.is_read,  # Добавляем статус, прочитано или нет
                }
            )


class CreateRoomUser(viewsets.ReadOnlyModelViewSet):

    queryset = Room.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def post(self, request, *args, **kwargs):
        """ Создание Thread and add users
        """
        logging.warning(request.data)        
        serializer = CreateRoomSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response({'data': serializer.data},
                            status=status.HTTP_201_CREATED
                            )

        return Response(
            {'data': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
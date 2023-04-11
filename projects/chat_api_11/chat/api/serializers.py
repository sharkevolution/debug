from rest_framework import serializers
from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from chat.models import Room, Message, TokenUser

from django.db.models import Q
from collections import OrderedDict


import logging
logger = logging.getLogger(__name__)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Save user token to base
        access_token_obj = token.access_token
        user_id = access_token_obj['user_id']
        cur_user = User.objects.get(id=int(user_id))

        # Добавить get or create 10/04/2023 если пользователь был но не создавался token
        acc = TokenUser.objects.get(user=cur_user)
        acc.token_access = str(token.access_token)
        acc.token_refresh = str(token)
        acc.save()

        # logging.warning('refresh: ' + str(token))
        # logging.warning('access: ' + str(str(token.access_token)))

        return token


class UserSerializer(serializers.ModelSerializer):
    """ Создание пользователя и токена
    """
    class Meta:
        model = User
        fields = ['username', 'password', 'token']

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)

        # ----- Добавляем токены в таблицу ----
        access_token_obj = refresh.access_token
        user_id = access_token_obj['user_id']

        cur_user = User.objects.get(id=int(user_id))
        acc = TokenUser.objects.create(user=cur_user)
        acc.token_access = str(refresh.access_token)
        acc.token_refresh = str(refresh)
        acc.save()
        # ----- Добавляем токены в таблицу ----

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
            instance.save()
            return instance


class UserListSerializer(serializers.ModelSerializer):
    """ Полечение списка id users
    """

    rooms = serializers.SerializerMethodField(method_name='related_rooms')

    class Meta:
        model = User
        ordering = ['id', 'rooms']
        fields = ['id', 'username', 'rooms']

    def related_rooms(self, obj):
        # filter related filed m2m
        related_rooms = obj.participante_in_room.filter()
        user_rooms = {}
        for b in related_rooms:
            user_rooms[b.id] = {'name': b.name}

        return OrderedDict(sorted(user_rooms.items(), key=lambda item: item[0]))


class UserDetailSerializer(serializers.ModelSerializer):
    """ одержання списку Thread'ів для будь-якого user'a (у кожному Thread'e має лежати
        останнє повідомлення, якщо таке є);
    """

    rooms = serializers.SerializerMethodField(method_name='related_rooms')

    class Meta:
        model = User
        ordering = ['id', 'rooms']
        fields = ['id', 'username', 'rooms']

    def related_rooms(self, obj):
        # filter related filed m2m
        related_rooms = obj.participante_in_room.filter()
        user_rooms = {}
        logging.warning(related_rooms)
        for b in related_rooms:

            related_messages = obj.from_user.filter()
            user_content = related_messages.filter(Q(room=b.id)
                                                   & (Q(user=obj.id) | Q(recipient=obj.id))).order_by('created')

            last_text_content = None
            last_text_is_read = None
            last_text_created = None
            last_text_pecipient = None
            last_text_status = None

            # Исправить так как тянет по obj.from_user не все данные захватывает!! 12.04.2023

            if user_content:
                usm = user_content[0]
                last_text_content = usm.content
                last_text_is_read = usm.is_read
                last_text_created = usm.created.strftime('%Y-%m-%d %H:%M:%S')
                last_text_pecipient = usm.recipient.username
                last_text_status = usm.status_text

                user_rooms[b.id] = {'name': b.name,
                                    'last_message_content': last_text_content,
                                    'last_message_is_read': last_text_is_read,
                                    'last_message_created': last_text_created,
                                    'last_message_recipient': last_text_pecipient,
                                    'last_message_status': last_text_status, }

        return OrderedDict(sorted(user_rooms.items(), key=lambda item: item[0]))


class UserUnreadDetailSerializer(serializers.ModelSerializer):
    """ непрочитанные сообщения пользователем

    """
    unread = serializers.SerializerMethodField(method_name='related_rooms_unread')

    class Meta:
        model = User
        fields = ['id', 'unread']

    def related_rooms_unread(self, obj):
        # filter related filed m2m
        
        related_rooms = obj.participante_in_room.filter()
        user_rooms = {}
        
        for b in related_rooms:
            
            related_messages = obj.from_user.filter()
            user_content = related_messages.filter(Q(room=b.id)
                                                   & (Q(user=obj.id) | Q(recipient=obj.id))).order_by('-created')

            if user_content:
                user_rooms[b.id] = {'name': b.name, 'unread': len(user_content)}

        return user_rooms


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']


class UserListingField(serializers.RelatedField):
    """
        Добавление информации о пользователях User
    """

    def to_representation(self, value):
        return {'id': value.id, 'name': value.username, 'is_staff': value.is_staff}


class RoomDetailSerializer(serializers.ModelSerializer):
    """ Детальная информация о Thread
    """
    participante = UserListingField(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'participante',
                  'created', 'updated', 'limit_users']


class RoomContentDetailSerializer(serializers.ModelSerializer):
    """ Список сообщений Thread
    """
    messages = serializers.SerializerMethodField(method_name='get_messages')

    class Meta:
        model = Room
        fields = ['id', 'name', 'messages']

    def get_messages(self, obj):
        # filter related filed m2m
        room_messages = {}
        mes = Message.objects.filter(room=obj.id).order_by("room")
        if mes:
            for b in mes:
                room_messages[b.id] = {'id': b.id, 'user': b.user.username,
                                       'repicient': b.recipient.username,
                                       'status_text': b.status_text, 'room': str(b.room.name),
                                       'content': b.content, 'created_iso': b.is_read,
                                       'created': b.created.strftime('%Y-%m-%d %H:%M:%S')}

        return OrderedDict(sorted(room_messages.items(), key=lambda item: item[0], reverse=True))


class SendMessagesSerializer(serializers.ModelSerializer):
    '''
        Реализовать сохранение в базу и отправку уведомления о новом сообщении
        Проверить и сделать валидацию 26.03.2023
    '''
    class Meta:
        model = Room
        fields = ['name']

    def sendmessage(self, validated_data):
        id_room = validated_data.pop('name', None)
        instance = self.Meta.model(**validated_data)
        logging.warning('ok api')
        if id_room:
            # instance.(id_room)
            # instance.save()
            return instance

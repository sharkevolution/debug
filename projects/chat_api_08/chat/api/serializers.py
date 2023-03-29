from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from chat.models import Room, Message, CustomUser

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


import logging
logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'token')

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        
        # Добавляем токены в связанную таблицу ----
        access_token_obj = refresh.access_token
        user_id = access_token_obj['user_id']   
        
        cur_user = User.objects.get(id=int(user_id))
        acc = CustomUser.objects.create(user=cur_user)
        acc.token_access = str(refresh.access_token)
        acc.token_refresh = str(refresh)
        acc.save()
        # ----- Добавляем токены в связанную таблицу ----

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


class MesageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'content', 'user', 'room_name', 'timestamp']


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = ['name', 'online', 'get_online_count']


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



    # channel_layer = get_channel_layer()
    # print("user.id {}".format(self.user.id))
    # print("user.id {}".format(self.recipient.id))

    # async_to_sync(channel_layer.group_send)("{}".format(self.user.id), notification)
    # async_to_sync(channel_layer.group_send)("{}".format(self.recipient.id), notification)
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.models import TokenUser

from chat.models import Room, Message, CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'token')

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)

        # cust = TokenUser()
        # print(str(cust.id))

        # cust = CustomUser(user.id)
        # cust.token_access = str(refresh.access_token)
        # cust.save()

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
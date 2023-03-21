from rest_framework import serializers
from chat.models import Room, Message


class MesageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'content', 'user', 'room_name', 'timestamp']


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = ['name', 'online', 'get_online_count']
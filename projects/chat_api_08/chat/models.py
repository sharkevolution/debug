# chat/models.py
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class CustomUser(models.Model):
    ''' 
        Tokens simple JWL, access, refresh
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
        
    token_access = models.TextField(max_length=255, null=True, blank=True)
    token_refresh =  models.TextField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.user.username



class Room(models.Model):  # Thread
    name = models.CharField(max_length=128)     
    participante = models.ManyToManyField(to=User, blank=True, through='ParticipanteRoom')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def get_online_count(self):
        return self.participante.count()

    def join(self, user):
        self.participante.add(user)
        self.save()

    def leave(self, user):
        pass
        # self.online.remove(user)
        # self.save()
    
    def display_room(self):
        """
        Creates a string for the Room. This is required to display room in Admin.
        """
        return ', '.join([ n.username for n in self.participante.all() ])

    def __str__(self):
        return f'{self.name} ({self.participante.count()})'


class ParticipanteRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user_status = models.CharField(max_length=25, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    readonly_fields = ('id',)

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user', 
                                related_name='from_user', db_index=True)
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='recipient', 
                                related_name='to_user', db_index=True)
    # recipient = models.CharField(max_length=50, null=True, blank=True)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)  # thread

    content = models.CharField(max_length=512)
    status_text = models.CharField(max_length=50, null=True, blank=True)  # Статус сообщения (private or public)
    is_read = models.DateTimeField(auto_now_add=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def last_name(self):
        return self.user.last_name

    def first_name(self):
        return self.user.first_name

    def room_name(self):
        return self.room.name

    def __str__(self):
        return f'{self.user}: {self.content} [{self.timestamp}]'

    class Meta:
        ordering = ["room"]

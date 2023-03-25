# chat/models.py
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
        
    token_access = models.TextField(max_length=255, null=True, blank=True)
    token_refresh =  models.TextField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.user.username



class Room(models.Model):
    name = models.CharField(max_length=128)
    online = models.ManyToManyField(to=User, blank=True)

    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        return f'{self.name} ({self.get_online_count()})'

    class Meta:
        ordering = ["name"]


class Message(models.Model):
    readonly_fields = ('id',)

    # user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user', related_name='from_user', db_index=True)
    # recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='recipient', related_name='to_user', db_index=True)
    recipient = models.CharField(max_length=50, null=True, blank=True) 

    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    status_text = models.CharField(max_length=50, null=True, blank=True)  # Статус сообщение (private or public)
    
    content = models.CharField(max_length=512)
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
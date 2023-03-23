# chat/admin.py

from django.contrib import admin
from .models import Room, Message, CustomUser

admin.site.register(CustomUser)

admin.site.register(Room)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'room_name', 'first_name', 'last_name', 'content', 'timestamp')
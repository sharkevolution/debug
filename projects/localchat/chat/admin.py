# chat/admin.py

from django.contrib import admin

from .models import Room, Message, User

admin.site.register(Room)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'content', 'timestamp')
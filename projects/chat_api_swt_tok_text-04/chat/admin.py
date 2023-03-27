# chat/admin.py

from django.contrib import admin
from .models import Room, Message, CustomUser
from django.utils.html import format_html

admin.site.register(Room)
# admin.site.register(CustomUser)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):

    fieldsets = (
        ('Токены пользователя', {
            'classes': ['wide'],
            'fields': ('user', 'token_access', 'token_refresh')
        }),    
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_to', 'status_text', 'room_name', 'content', 'timestamp')
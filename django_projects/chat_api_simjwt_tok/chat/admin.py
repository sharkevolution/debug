# chat/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Room, Message, User

class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff',
        )


admin.site.register(User, CustomUserAdmin)


admin.site.register(Room)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'room_name', 'first_name', 'last_name', 'content', 'timestamp')
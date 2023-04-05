# chat/admin.py

from django.contrib import admin
from .models import Room, Message, TokenUser, OnlineParticipanteRoom, CursorParticipanteRoom

# admin.site.register(Room)
# admin.site.register(CustomUser)


@admin.register(OnlineParticipanteRoom)
class OnlineParticipanteRoomAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'user_status', 'timestamp')


class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_users', 'limit_users')
    # readonly_fields = ('created', )
    # fields = ('name', 'participante', 'updated', 'created')


admin.site.register(Room, RoomAdmin)


@admin.register(TokenUser)
class TokenUserAdmin(admin.ModelAdmin):

    fieldsets = (
        ('Токены пользователя', {
            'classes': ['wide'],
            'fields': ('user', 'token_access', 'token_refresh')
        }),    
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    @admin.display(description='created_iso')
    def admin_created(self, obj):
        return obj.created.strftime('%Y-%m-%d %H:%M:%S')

    list_display = ('id', 'user', 'recipient', 'status_text', 'room_name', 'content', 'is_read', 'admin_created')
    
    
@admin.register(CursorParticipanteRoom)
class CursorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'room', 'cursor_message_id')
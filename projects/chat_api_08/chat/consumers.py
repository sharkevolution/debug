# chat/consumers.py

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Room, Message, User, ParticipanteRoom  # new import

import logging
logger = logging.getLogger(__name__)

class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None  # new
        self.user_id = None # Sitala
        self.user_inbox = None  # new

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = Room.objects.get(name=self.room_name)
        self.user = self.scope['user']  # new
        self.user_id = self.scope["session"]["_auth_user_id"]  # Sitala
        self.user_inbox = f'inbox_{self.user.username}'  # new

        # connection has to be accepted
        self.accept()

        if self.user.is_authenticated:
            # -------------------- new --------------------
            # create a user inbox for private messages
            async_to_sync(self.channel_layer.group_add)(
                self.user_inbox,
                self.channel_name,
            )

        # join the room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        # send the user list to the newly joined user
        self.send(json.dumps({
            'type': 'user_list',
            'users': [user.username for user in self.room.participante.all()],
        }))

        if self.user.is_authenticated:
            # send the join event to the room
            user_obg_list = User.objects.all()

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'user': self.user.username,  # Имя user присоединяющегося
                    'user_list': [b.username for b in user_obg_list],  # Список пользователей
                    'username_admin': '',
                }
            )
            logging.warning('paticipante add to room' + str(self.user))
            r1 = Room.objects.get(name=self.room_name)
            u1 = User.objects.get(username=self.user)
            super_part = ParticipanteRoom.objects.create(user=u1, room=r1, user_status='off')
            super_part.save()
            
            # self.room.participante.add(self.user)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

        if self.user.is_authenticated:
            # -------------------- new --------------------
            # delete the user inbox for private messages
            async_to_sync(self.channel_layer.group_discard)(
                self.user_inbox,
                self.channel_name,
            )

        if self.user.is_authenticated:
            # send the leave event to the room
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': self.user.username,
                }
            )
            # self.room.participante.remove(self.user)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        logger.warning('Consumers.py Разбираем сообщение для отправки пользователю: ' + message)

        if not self.user.is_authenticated:  # new
            return                          # new

        # -------------------- new --------------------
        if message.startswith('/pm '):
            split = message.split(' ', 2)
            target = split[1]
            target_msg = split[2]

            # send private message to the target
            async_to_sync(self.channel_layer.group_send)(
                f'inbox_{target}',
                {
                    'type': 'private_message',
                    'user': self.user.username,
                    'message': target_msg,
                }
            )
            # send private message delivered to the user
            self.send(json.dumps({
                'type': 'private_message_delivered',
                'target': target,
                'message': target_msg,
            }))

            user_destination = User.objects.get(username=target)

            # Сохраняем запись, private
            Message.objects.create(user=self.user, recipient=user_destination, 
                                    status_text='private', 
                                    room=self.room, content=message)

            return
        # ---------------- end of new ----------------

        # send chat message event to the room
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': self.user.username,  # new
                'message': message,
            }
        )
        # Сохраняем запись, public
        Message.objects.create(user=self.user, recipient=self.user, 
                                    status_text='public', 
                                    room=self.room, content=message)

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def user_join(self, event):

        logging.warning('Consumers.py user_join: ' + json.dumps(event))
        
        self.send(text_data=json.dumps(event))

    def user_leave(self, event):
        self.send(text_data=json.dumps(event))
    
    def private_message(self, event):
        self.send(text_data=json.dumps(event))

    def private_message_delivered(self, event):
        self.send(text_data=json.dumps(event))




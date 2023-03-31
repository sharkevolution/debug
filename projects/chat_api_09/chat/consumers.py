# chat/consumers.py

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Room, Message, User, OnlineParticipanteRoom

import logging
logger = logging.getLogger(__name__)


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None  # new
        self.user_id = None  # Sitala
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
                    # Список пользователей
                    'user_list': [b.username for b in user_obg_list],
                    'username_admin': '',
                }
            )
            logging.warning('paticipante add to room' + str(self.user))
            self.user_save_status_online(self.user, 'on')

            self.room.participante.add(self.user)
            self.room.save()

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
            self.user_save_status_online(self.user, 'offline')

    def receive(self, text_data=None, bytes_data=None):

        text_data_json = json.loads(text_data)

        if participantes := text_data_json.get('participantes'):
            if user_add_room := participantes.get('userAddRoom'):
                for user_name in user_add_room:
                    u1 = User.objects.get(username=user_name)
                    self.room.participante.add(u1)
                    self.room.save()

                    self.user_save_status_online(user_name, 'offline')
                    logging.warning('Users add to room: ' + user_name)

            if user_remove_room := participantes.get('userRemoveRoom'):
                for user_name in user_remove_room:
                    u1 = User.objects.get(username=user_name)

                    if not self.user.username == user_name:
                        self.room.participante.remove(u1)
                        self.room.save()

                        self.user_save_status_online(user_name, 'offline')
                        logging.warning('Users remove from room: ' + user_name)

                        async_to_sync(self.channel_layer.group_send)(
                            f'inbox_{user_name}',
                            {
                                'type': 'private_quit',
                                'user': user_name,
                                'message': user_name
                            }
                        )

                        async_to_sync(self.channel_layer.group_send)(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'user': self.user.username,  # new
                                'message': f'{user_name} was Delete from this room...',
                            }
                        )

                    else:
                        logging.warning(
                            'Users Not remove from room: ' + user_name)

            # send chat message event Update to the room
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_update',
                    'users': [user.username for user in self.room.participante.all()],
                }
            )
            return

        if message := text_data_json.get('message'):

            logger.warning(
                'Consumers.py Разбираем сообщение для отправки пользователю: ' + message)

            if not self.user.is_authenticated:  # new
                return                          # new

            # -------------------- new --------------------
            if message.startswith('/pm '):
                split=message.split(' ', 2)
                target=split[1]
                target_msg=split[2]

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

                user_destination=User.objects.get(username=target)

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

    def user_save_status_online(self, user_name, status):

        r1=Room.objects.get(name=self.room_name)
        u1=User.objects.get(username=user_name)
        super_part=OnlineParticipanteRoom.objects.create(
                            user=u1, room=r1, user_status=status)
        super_part.save()

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

    def user_update(self, event):
        self.send(text_data=json.dumps(event))

    def private_quit(self, event):
        self.send(text_data=json.dumps(event))

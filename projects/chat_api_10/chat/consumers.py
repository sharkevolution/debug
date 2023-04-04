# chat/consumers.py

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Room, Message, User, OnlineParticipanteRoom

import logging
logger = logging.getLogger(__name__)


class ChatConsumer(WebsocketConsumer):

    starting_server = 0  # Первый запуск сервера для

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None
        self.user_id = None
        self.user_inbox = None

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = Room.objects.get(name=self.room_name)
        self.user = self.scope['user']  # new
        self.user_id = self.scope["session"]["_auth_user_id"]  # Sitala
        self.user_inbox = f'inbox_{self.user.username}'  # new

        ChatConsumer.starting_server += 1
        if ChatConsumer.starting_server == 1:
            # Принудительное обновление статусов на offline при первом запуске сервера
            # Для отображения корекктных статусов кто в не в сети.
            self.reset_participants_status()

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
            logging.warning('paticipante add to room' + str(self.user))
            self.user_save_status_online(self.user, 'on')
            self.room.participante.add(self.user)
            self.room.save()

            # send the join event to the room
            user_obg_list = User.objects.all()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'user': self.user.username,  # Имя user присоединяющегося
                    # Список всех пользователей
                    'contacts': [b.username for b in user_obg_list],
                }
            )
            # send participantes status
            current_users_status = self.get_last_status_users()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                'type': 'user_list',
                'participantes': current_users_status,
                }
            )

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
            # send the leave event to the room and Update status on/off
            self.user_save_status_online(self.user, 'offline')
            current_users_status = self.get_last_status_users()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': self.user.username,
                    'participantes': current_users_status,  # Исправить статусы и название развести
                }
            )

    def receive(self, text_data=None, bytes_data=None):

        text_data_json = json.loads(text_data)

        if participantes := text_data_json.get('participantes'):
            if user_add_room := participantes.get('userAddRoom'):
                # добавление в комнату
                for user_name in user_add_room:
                    u1 = User.objects.get(username=user_name)
                    self.room.participante.add(u1)
                    self.room.save()

                    # Update status on/off
                    self.user_save_status_online(user_name, 'offline')
                    # logging.warning('Users add to room: ' + user_name)

            if user_remove_room := participantes.get('userRemoveRoom'):
                # Удаление из комнаты
                for user_name in user_remove_room:
                    u1 = User.objects.get(username=user_name)

                    if not self.user.username == user_name:
                        logging.warning('Delete: ' + self.room.name)
                        self.room.participante.remove(u1)
                        self.room.save()

                        # logging.warning('Users remove from room: ' + user_name)

                        # Отправляем клиенту команду на выход из комнаты
                        async_to_sync(self.channel_layer.group_send)(
                            f'inbox_{user_name}',
                            {
                                'type': 'private_quit',
                                'user': user_name,
                                'room': self.room.name
                            }
                        )
                        # Пишем в чат сообщение об удалении из комнаты
                        async_to_sync(self.channel_layer.group_send)(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'user': self.user.username,  # new
                                'message': f'{user_name} was Delete from this room...',
                            }
                        )
                    else:
                        pass

            # send chat message event Update to the room
            current_users_status = self.get_last_status_users()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_update',
                    'participantes': current_users_status,
                }
            )
            return

        if message := text_data_json.get('message'):

            if not self.user.is_authenticated:  # new
                return                          # new

            # Если в комнате всего 2 участника, делаем сообщение частным
            participantes_count = self.room.get_participante_count()
            if participantes_count == 2:
                logging.warning(f'Participante count: {participantes_count}')
                if not message.startswith('/pm '):
                    # Всего Два участника, поэтому, делаем сообщение частным,
                    second_user = [ n.username for n in self.room.participante.all() if not n.username == self.user.username]
                    message = ''.join(['/pm ', second_user[0], " ", message])
                    logging.warning('Extra: ' + message)

            # -------------------- new --------------------
            if message.startswith('/pm '):
                split = message.split(' ', 2)
                target = split[1]
                target_msg = split[2]

                # Сохраняем запись, private
                user_destination = User.objects.get(username=target)
                Message.objects.create(user=self.user, recipient=user_destination,
                                       status_text='private',
                                       room=self.room, content=message)

                once_text = Message.objects.filter(user=self.user, recipient=user_destination, status_text='private', 
                                            room=self.room, content=message).order_by("created")
                last_text = once_text.last()
                logging.warning(last_text.id)

                # send private message to the target
                async_to_sync(self.channel_layer.group_send)(
                    f'inbox_{target}',
                    {
                        'type': 'private_message',
                        'user': self.user.username,
                        'message': target_msg,
                        'message_id': last_text.id,
                        'message_status': last_text.is_read,  # Добавляем статус прочитано или нет
                    }
                )
                
                # send private message delivered to the user
                self.send(json.dumps({
                    'type': 'private_message_delivered',
                    'target': target,
                    'message': target_msg,
                    'message_id': last_text.id,
                    'message_status': last_text.is_read,  # Добавляем статус, прочитано или нет
                }))

                return
            # ---------------- end of new ----------------

            # Сохраняем запись, Public messages
            Message.objects.create(user=self.user, recipient=self.user,
                                   status_text='public',
                                   room=self.room, content=message)


            once_text = Message.objects.filter(user=self.user, recipient=self.user, status_text='public', 
                                            room=self.room, content=message).order_by("created")
            last_text = once_text.last()
            logging.warning(last_text.id)
            # send chat message event to the room
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'user': self.user.username,  # new
                    'message': message,
                    'message_id': last_text.id,
                    'message_status': False,  # публичная комната участник 1 или больше > 2
                }
            )

        if echo := text_data_json.get('echo'):
            # send private Echo Username to the target
            async_to_sync(self.channel_layer.group_send)(
                f'inbox_{self.user.username}',
                {
                    'type': 'user_echo',
                    'user': self.user.username,
                    }
            )
        
        if messages_is_read := text_data_json.get('messages_is_read'):
            # Get status 'is_read' messages and Update into base
            logging.warning('I am function messages_is_read: ' + str(messages_is_read))
            for b in messages_is_read:
                pk = b.split('-')
                if pk[1].isnumeric():
                    try:
                        whois_message = Message.objects.get(id=int(pk[1]))
                        you_ = self.user.username
                        from_ = whois_message.user
                        to_ = whois_message.recipient

                        if not you_ == from_ and you_ == to_:
                            # частное сообщение
                            # наблюдатель (you) не равен от кого (from) и (you) равен (to)  
                            Message.objects.filter(id=int(pk[1])).update(is_read=True)
                        # if from_ == to_:
                        #     # Сообщение публичное для группы
                        #     pass

                        logging.warning(f'You: {self.user.username}: {str(b)}')
                        logging.warning(f'from_: {from_}')
                        logging.warning(f'to_: {to_}')
                    except Exception as ex:
                        logging.warning(ex)
                        logging.warning(f'number box: {b}')

    def get_last_status_users(self):
        """
            Get last status user (on/offline)
        """
        current_users_status={}
        user_room_list=self.room.participante.all()
        for b in user_room_list:
            user_history=OnlineParticipanteRoom.objects.filter(user=b.id,
                                                                    room=self.room).order_by("timestamp")
            if h := user_history.last():
                curstat=h.user_status
            else:
                curstat='offline'
            current_users_status[b.username]=curstat

        return current_users_status

    def user_save_status_online(self, user_name, status):
        """
            Update status on/off
        """
        r1=Room.objects.get(name=self.room_name)
        u1=User.objects.get(username=user_name)
        super_part=OnlineParticipanteRoom.objects.create(
                            user=u1, room=r1, user_status=status)
        super_part.save()

    def reset_participants_status(self):
        """
            При первом запуске сервера, принудительный сброс статусов участников на offline
        """
        allRooms=Room.objects.all()
        for cr in allRooms:
            r1=Room.objects.get(name=cr.name)
            user_room_list=r1.participante.all()
            for u1 in user_room_list:
                u1=User.objects.get(username=u1.username)
                super_part=OnlineParticipanteRoom.objects.create(
                    user=u1, room=r1, user_status='offline')
                super_part.save()

    def get_messages_open_page(self):
        """
            Выборка последних 10 сообщений пользователя при входе в комнату
            с разделением на прочитанные и не прочитанные
        """
        pass

    def user_echo(self, event):
        # Send echo username
        self.send(text_data=json.dumps(event))

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def user_list(self, event):
        self.send(text_data=json.dumps(event))

    def user_join(self, event):
        self.send(text_data=json.dumps(event))

    def user_leave(self, event):
        self.send(text_data=json.dumps(event))

    def private_message(self, event):
        self.send(text_data=json.dumps(event))

    def private_message_delivered(self, event):
        self.send(text_data=json.dumps(event))

    def user_update(self, event):
        # Отправка команды обновления списка участников
        self.send(text_data=json.dumps(event))

    def private_quit(self, event):
        # Отправка команды клиенту на выход из комнаты
        self.send(text_data=json.dumps(event))

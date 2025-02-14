from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

class ChatSideBarConsumer(AsyncWebsocketConsumer):
    """Потребитель для личных чатов"""

    async def connect(self):
        """Установка соединения между клиентом и сервером для личного чата"""
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'personal_chat_{self.username}'

        # Подключение к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Отключение от личного чата"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Сервер получает сообщение от клиента через WS"""
        data = json.loads(text_data)

        if data['action'] == 'send_message':
            # Импортируем модели здесь для избежания ошибки App loaded Yet.
            from chat.models import Chat, Message
            # Создание нового чата, если его еще нет
            chat, created = await database_sync_to_async(Chat.objects.get_or_create)(
                user1=self.scope['user'],
                user2=data['user2_id'],
            )
            # Создание нового сообщения
            message = await database_sync_to_async(Message.objects.create)(
                chat=chat,
                sender=self.scope['user'],
                content=data['message']
            )
            await self.send_message_update(message)

            if created:  # Если чат был создан
                chat_data = {
                    'id': chat.id,
                    'user_username': chat.user2.username,
                    'user_avatar': chat.user2.photo.url,
                    'unread_count': 0,  # Или другое значение по умолчанию
                }
                await self.create_chat(chat_data)

    # async def chat_message(self, event):
    #     """Новое сообщение в чате"""
    #     message = event['message']
    #     username = event['username']
    #     avatar_url = event['avatar_url']
    #
    #     # Отправка данных клиенту (в JSON)
    #     await self.send(text_data=json.dumps({
    #         'message': message,
    #         'username': username,
    #         'avatar_url': avatar_url
    #     }))

    async def chat_message(self, event):
        """Обработка нового сообщения в чате"""
        message_data = event['message']  # Это должно быть словарем
        username = event.get('username')  # Используйте get для избежания KeyError
        avatar_url = event.get('avatar_url')  # Используйте get для избежания KeyError

        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'chat_id': message_data.get('chat_id'),
            'message': message_data['content'],
            'username': username,  # Теперь это безопасно
            'avatar_url': avatar_url,  # Теперь это безопасно
        }))

    async def create_chat(self, chat_data):
        """Создание нового чата и отправка обновления всем участникам"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_created',
                'chat_data': chat_data,
            }
        )

    async def send_message_update(self, message):
        """Отправка обновления сообщения всем участникам личного чата"""
        message_data = {
            'chat_id': message.chat.id,
            'message': message.content,
            'username': message.sender.username,
            'avatar_url': message.sender.avatar.url,
            'user2_username': message.chat.user2.username,
            'user2_avatar': message.chat.user2.photo.url,
            'unread_count': await self.get_unread_count(message.chat),
        }
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new_message',
                'message': message_data,
            }
        )

    async def new_message(self, event):
        """Обновление информации о новом сообщении в личном чате"""
        message_data = event['message']
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'chat_id': message_data['chat_id'],
            'message': message_data['message'],
            'username': message_data['username'],
            'avatar_url': message_data['avatar_url'],
        }))

    async def send_chat_creation_update(self, chat_data):
        """Создание нового чата и отправка обновления всем участникам"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_created',
                'chat_data': chat_data,
            }
        )

    async def chat_created(self, event):
        """Обработка события создания нового чата"""
        chat_data = event['chat_data']
        await self.send(text_data=json.dumps({
            'type': 'chat_created',
            'chat_data': chat_data,
        }))

    async def delete_chat(self, chat_id):
        """Удаление чата и отправка обновления всем участникам"""
        # Удаление чата из базы данных
        await database_sync_to_async(Chat.objects.filter(id=chat_id).delete)()

        # Отправка обновления всем участникам
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_deleted',
                'chat_id': chat_id,
            }
        )

    async def chat_deleted(self, event):
        """Обработка события удаления чата"""
        chat_id = event['chat_id']
        await self.send(text_data=json.dumps({
            'type': 'chat_deleted',
            'chat_id': chat_id,
        }))

    async def chat_updated(self, event):
        """Обработка обновления чата"""
        chat_data = event['chat_data']
        await self.send(text_data=json.dumps({
            'type': 'chat_updated',
            'chat_data': chat_data,
        }))

class GroupSideBarConsumer(AsyncWebsocketConsumer):
    """Потребитель для групповых чатов"""

    async def connect(self):
        """Установка соединения между клиентом и сервером для группового чата"""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'group_chat_{self.room_name}'

        # Подключение к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Отключение от группового чата"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Сервер получает сообщение от клиента через WS для группового чата"""
        data = json.loads(text_data)

        if data['action'] == 'send_message':
            # Импортируем модели здесь для избежания ошибки App loaded Yet.
            from chat.models import Group, Message
            # Получение группы по ID
            group = await database_sync_to_async(Group.objects.get)(id=data['group_id'])
            # Создание нового сообщения
            message = await database_sync_to_async(Message.objects.create)(
                group=group,
                sender=self.scope['user'],
                content=data['message']
            )
            await self.send_group_update(message)

    async def send_group_update(self, message):
        """Отправка обновления сообщения всем участникам группового чата"""
        message_data = {
            'group_id': message.group.id,
            'message': message.content,
            'username': message.sender.username,
            'avatar_url': message.sender.avatar.url,
        }
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'group_message',
                'message': message_data,
            }
        )

    async def group_message(self, event):
        """Обновление информации о новом сообщении в групповом чате"""
        message_data = event['message']
        await self.send(text_data=json.dumps({
            'type': 'group_message',
            'group_id': message_data['group_id'],
            'message': message_data['message'],
            'username': message_data['username'],
            'avatar_url': message_data['avatar_url'],
        }))

    async def group_created(self, event):
        """Обработка события создания группы"""
        group_data = event['group_data']
        await self.send(text_data=json.dumps({
            'type': 'group_created',
            'group_data': group_data,
        }))

    async def group_deleted(self, event):
        """Обработка события удаления группы"""
        group_id = event['group_id']
        await self.send(text_data=json.dumps({
            'type': 'group_deleted',
            'group_id': group_id,
        }))
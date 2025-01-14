import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import Message, Group
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"Connected to {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("Received message:", text_data)
        try:
            from .models import Message, Group
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            username = text_data_json['username']
            avatar_url = text_data_json['avatar_url']

            group = await database_sync_to_async(Group.objects.get)(id=self.room_name)

            await database_sync_to_async(Message.objects.create)(
                sender=self.scope["user"],
                content=message,
                group=group
            )
            print(f"Message saved: {message}")

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'avatar_url': avatar_url
                }
            )
            print(f"Message sent to group {self.room_group_name}: {message}")
        except Exception as e:
            print(f"Error in receive: {e}")

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        avatar_url = event['avatar_url']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'avatar_url': avatar_url
        }))

# Добавьте этот класс для обработки личных чатов
class PersonalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import CustomUser
        self.username = self.scope['url_route']['kwargs']['username']
        self.user = self.scope['user']

        # Уникальное имя группы для каждого пользователя
        self.room_group_name = f'personal_chat_{self.user.username}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"Connected to {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("Received personal message:", text_data)
        try:
            from .models import Message, CustomUser, Chat
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            username = text_data_json['username']
            avatar_url = text_data_json['avatar_url']

            # Получаем пользователя, которому отправлено сообщение
            receiver = await database_sync_to_async(CustomUser.objects.get)(username=self.username)

            # Убедитесь, что порядок пользователей правильный
            if self.user.username < receiver.username:
                user1 = self.user
                user2 = receiver
            else:
                user1 = receiver
                user2 = self.user

            # Получаем или создаем чат между пользователями
            chat, created = await database_sync_to_async(Chat.objects.get_or_create)(
                user1=user1,
                user2=user2
            )

            # Сохраняем личное сообщение в базе данных
            await database_sync_to_async(Message.objects.create)(
                sender=self.user,
                receiver=receiver,  # Указываем получателя
                content=message,
                chat=chat,
            )
            print(f"Personal message saved: {message}")

            # Отправляем сообщение в группу получателя
            receiver_group_name = f'personal_chat_{receiver.username}'
            await self.channel_layer.group_send(
                receiver_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'avatar_url': avatar_url
                }
            )
        except Exception as e:
            print(f"Error in receive: {e}")

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        avatar_url = event['avatar_url']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'avatar_url': avatar_url
        }))
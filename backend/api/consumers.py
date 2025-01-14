from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Логика подключения
        await self.accept()

    async def disconnect(self, close_code):
        # Логика отключения
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Импортируем модели и сериализаторы здесь
        from chat.models import Chat, Group
        from .serializers import ChatSerializer, GroupSerializer

        # Логика обработки сообщений
        if data['action'] == 'send_message':
            # Создание нового чата, если его еще нет
            chat, created = await database_sync_to_async(Chat.objects.get_or_create)(
                user2=data['user2_id']
            )
            chat_data = ChatSerializer(chat).data
            await self.send_chat_update(chat_data)

        elif data['action'] == 'create_group':
            # Создание новой группы
            group = await database_sync_to_async(Group.objects.create)(name=data['group_name'])
            group_data = GroupSerializer(group).data
            await self.send_group_update(group_data)

    async def send_chat_update(self, chat_data):
        await self.channel_layer.group_send(
            'chat_group',  # Название группы, в которую отправляем
            {
                'type': 'chat_message',
                'chat': chat_data,
            }
        )

    async def send_group_update(self, group_data):
        await self.channel_layer.group_send(
            'group_group',  # Название группы, в которую отправляем
            {
                'type': 'group_message',
                'group': group_data,
            }
        )

    async def chat_message(self, event):
        chat_data = event['chat']
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'chat': chat_data,
        }))

    async def group_message(self, event):
        group_data = event['group']
        await self.send(text_data=json.dumps({
            'type': 'group',
            'group': group_data,
        }))
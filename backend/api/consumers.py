from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.db.models import Q

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Логика подключения
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Подключение к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Логика отключения
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Импортируем модели и сериализаторы здесь
        from chat.models import Chat, Group, Message
        from .serializers import ChatSerializer, GroupSerializer

        # Логика обработки сообщений
        if data['action'] == 'send_message':
            # Создание нового чата, если его еще нет
            chat, created = await database_sync_to_async(Chat.objects.get_or_create)(
                user2=data['user2_id']
            )
            # Создание нового сообщения
            message = await database_sync_to_async(Message.objects.create)(
                chat=chat,
                sender=self.scope['user'],
                content=data['message']
            )
            # Отправка обновлений
            await self.send_message_update(message)

        elif data['action'] == 'create_group':
            # Создание новой группы
            group = await database_sync_to_async(Group.objects.create)(name=data['group_name'])
            group_data = GroupSerializer(group).data
            await self.send_group_update(group_data)

    async def send_message_update(self, message):
        message_data = {
            'chat_id': message.chat.id,  # Убедитесь, что вы передаете chat_id
            'message': message.content,
            'username': message.sender.username,
            'avatar_url': message.sender.avatar.url,  # Предполагается, что у вас есть поле avatar
        }
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new_message',
                'message': message_data,
            }
        )

    async def send_chat_update(self, chat_data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'chat': chat_data,
            }
        )

        # Отправляем обновлённый список чатов
        updated_chats = await self.get_updated_chats()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_chat_list',
                'chats': updated_chats,
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

        # Отправляем обновлённый список групп
        updated_groups = await self.get_updated_groups()
        await self.channel_layer.group_send(
            'group_group',
            {
                'type': 'update_group_list',
                'groups': updated_groups,
            }
        )

    @database_sync_to_async
    def get_updated_chats(self):
        # Импортируем модели и сериализаторы здесь
        from chat.models import Chat
        from .serializers import ChatSerializer

        # Получаем обновленный список чатов для текущего пользователя
        user = self.scope['user']
        chats = Chat.objects.filter(Q(user1=user) | Q(user2=user))
        return ChatSerializer(chats, many=True).data

    @database_sync_to_async
    def get_updated_groups(self):
        # Импортируем модели и сериализаторы здесь
        from chat.models import Chat
        from .serializers import ChatSerializer

        # Получаем обновленный список групп для текущего пользователя
        user = self.scope['user']
        groups = Group.objects.filter(members=user)
        return GroupSerializer(groups, many=True).data

    async def update_chat_list(self, event):
        # Обработка новых типов сообщений для чатов
        chats = event['chats']
        await self.send(text_data=json.dumps({
            'type': 'update_chats',
            'chats': chats,
        }))

    async def update_group_list(self, event):
        # Обработка новых типов сообщений для групп
        groups = event['groups']
        await self.send(text_data=json.dumps({
            'type': 'update_groups',
            'groups': groups,
        }))

    async def chat_message(self, event):
        chat_data = event['chat']
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'chat': chat_data,
        }))

    async def new_message(self, event):
        message_data = event['message']
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'chat_id': message_data['chat_id'],  # Передаем chat_id для обновления интерфейса
            'message': message_data['message'],
            'username': message_data['username'],
            'avatar_url': message_data['avatar_url'],
        }))

    async def group_message(self, event):
        group_data = event['group']
        await self.send(text_data=json.dumps({
            'type': 'group',
            'group': group_data,
        }))
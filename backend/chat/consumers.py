from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

class PersonalChatConsumer(AsyncWebsocketConsumer):
    """Личная переписка - потребитель WS-соденинения"""
    async def connect(self):
        """Установка соединения между клиентом и сервером """
        from .models import CustomUser, Chat, Message # Импортируем модели здесь для избежания ошибки App loaded Yet.

        self.username = self.scope['url_route']['kwargs']['username'] # получение имени пользователя
        self.user = self.scope['user'] # группировка клиентов

        # Уникальное имя группы для каждого пользователя
        self.room_group_name = f'personal_chat_{self.user.username}'

        # Подключение к группе (добавление текущего канала в группу соответствующей комнаты)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Принятие соединения (сервер принимает WS-соединения, после этого клиент может начать обмен с сервером)
        await self.accept()

        print(f"Присоединение к {self.room_group_name}") # Отладка

    async def disconnect(self, close_code):
        """Отключение"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        ) # удаление текущего пользователя из группы

    async def receive(self, text_data):
        """Сервер получает соообщение от клиента через WS"""

        print("Получено личное сообщение:", text_data) # отладка

        # Обработка входящих данных
        try:
            from .models import Message, CustomUser, Chat
            text_data_json = json.loads(text_data) # преобразуем JSON-строку в Python-объект
            message = text_data_json['message']
            username = text_data_json['username']
            avatar_url = text_data_json['avatar_url']

            # Получаем пользователя, которому отправлено сообщение
            receiver = await database_sync_to_async(CustomUser.objects.get)(username=self.username)

            # Проверка порядка пользователей (для корректного отображения собеседника в разделе "Чаты")
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

            print(f"Личное сообщение сохранено: {message}") # отладка

            # Отправляем сообщение в группу получателя
            receiver_group_name = f'personal_chat_{receiver.username}'
            await self.channel_layer.group_send(
                receiver_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'content': message,
                        'chat_id': chat.id,
                    },
                    'username': username,
                    'avatar_url': avatar_url
                }
            )

            # После сохранения сообщения
            await self.send_sidebar_update(receiver, chat)

        except Exception as e:
            print(f"Ошибка при получении: {e}")

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


    async def send_sidebar_update(self, receiver, chat):
        """Отправка обновления в сайдбар для получателя"""
        chat_data = {
            'id': chat.id,
            'user_username': receiver.username,
            'user_avatar': receiver.photo.url,
            'unread_count': 1,  # Увеличиваем счетчик непрочитанных сообщений
        }

        print(f"Отправка события chat_created для {receiver.username}")
        await self.channel_layer.group_send(
            f'api_chat_sidebar_{receiver.username}',  # Уникальная группа для сайдбара
            {
                'type': 'chat_updated',
                'chat_data': chat_data,
            }
        )


class GroupChatConsumer(AsyncWebsocketConsumer):
    """Групповые чаты - потребители WS-соединения"""
    async def connect(self):
        """Установка соединения между клиентом и сервером"""
        from .models import Message, Group # Импортируем модели здесь для избежания ошибки App loaded Yet.

        self.room_name = self.scope['url_route']['kwargs']['room_name'] # получение имени комнаты
        self.room_group_name = f'chat_{self.room_name}' # группировка клиентов

        # Подключение к группе (добавление текущего канала в группу соответствующей комнаты)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Принятие соединения (сервер принимает WS-соединения, после этого клиент может начать обмен с сервером)
        await self.accept()

        # Отладка
        print(f"Присоединение к {self.room_group_name}")

    async def disconnect(self, close_code):
        """Отключение"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        ) # удаление текущего канала из группы

    async def receive(self, text_data):
        """Сервер получает сообщение от клиента через WS"""

        print("Полученное сообщение:", text_data) # отладка

        # Обработка входящих данных
        try:
            from .models import Message, Group
            text_data_json = json.loads(text_data) # преобразуем JSON-строку в Python-объект
            message = text_data_json['message']
            username = text_data_json['username']
            avatar_url = text_data_json['avatar_url']

            # Получаем группу
            group = await database_sync_to_async(Group.objects.get)(id=self.room_name)

            # Сохраняем сообщение
            message_instance = await database_sync_to_async(Message.objects.create)(
                sender=self.scope["user"],
                content=message,
                group=group
            )

            print(f"Сообщение сохранено: {message}") # отладка

            # Отправка сообщения в группу
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',  # Убедитесь, что тип сообщения правильный
                    'message': {  # Убедитесь, что это словарь
                        'content': message,
                        'chat_id': group.id,  # Или другой идентификатор группы
                    },
                    'username': username,
                    'avatar_url': avatar_url
                }
            )

            print(f"Сообщение отправлено в группу {self.room_group_name}: {message}")

        except Exception as e:
            print(f"Ошибка отправки: {e}")

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
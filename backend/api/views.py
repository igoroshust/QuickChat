from .serializers import ChatSerializer, GroupSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from chat.models import Chat, Group, Message
from django.db.models import Q
from django.http import Http404
from rest_framework.decorators import action
from rest_framework import status
# import logging
#
# logger = logging.getLogger(__name__)

class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для списка Чатов"""
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Фильтруем чаты, в которых участвует текущий пользователь"""
        return self.queryset.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        )

    def get_serializer_context(self):
        """Расширяем контекст для сериализатора Чата, добавляя объект запроса"""
        context = super().get_serializer_context()
        context['request'] = self.request
        context['current_chat_user'] = self.request.GET.get(
            'current_chat_user')  # Получаем текущего собеседника из параметров запроса
        return context

    @action(detail=False, methods=['post'], url_path='update-read-status')
    def update_read_status(self, request):
        current_chat_user = request.data.get('current_chat_user')
        if not current_chat_user:
            return Response({'error': 'Текущий собеседник не указан'}, status=status.HTTP_400_BAD_REQUEST)

        # Получаем чат, в котором участвует текущий пользователь и указанный собеседник
        chat = Chat.objects.filter(
            (Q(user1=request.user) & Q(user2=current_chat_user)) |
            (Q(user2=request.user) & Q(user1=current_chat_user))
        ).first()

        if chat:
            # Обновляем статус всех непрочитанных сообщений
            Message.objects.filter(chat=chat, receiver=request.user, is_read=False).update(is_read=True)

        return Response({'status': 'success'})

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для списка Групп"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Фильтруем группы, в которых участвует текущий пользователь"""
        return self.queryset.filter(members=self.request.user)

    def get_serializer_context(self):
        """Расширяем контекст для сериализатора Группы, добавляя объект запроса"""
        context = super().get_serializer_context()
        context['request'] = self.request  # Передаём текущий запрос в контекст
        context['current_group_id'] = self.request.GET.get('current_group_id')  # Получаем текущую группу из параметров запроса
        return context

class UpdateUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_chat_user = request.data.get('current_chat_user')
        if not current_chat_user:
            return Response({'error': 'Текущий собеседник не указан'}, status=400)

        # Сброс статуса непрочитанных сообщений
        Message.objects.filter(receiver=request.user, sender=current_chat_user, is_read=False).update(is_read=True)

        return Response({'status': 'success'})
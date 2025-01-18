from .serializers import ChatSerializer, GroupSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from chat.models import Chat, Group, Message
from django.db.models import Q
from django.http import Http404


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
        context['request'] = self.request # Передаём текущий запрос в контекст
        return context

class MarkMessagesAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_chat_user = request.GET.get('current_chat_user')
        if not current_chat_user:
            return Response({'error': 'Пользователь не указан'}, status=400)

        # Обновляем все непрочитанные сообщения для текущего пользователя
        Message.objects.filter(receiver=request.user, sender__username=current_chat_user, is_read=False).update(is_read=True)

        return Response({'status': 'success'})
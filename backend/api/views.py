from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from chat.models import Chat, Group
from .serializers import ChatSerializer, GroupSerializer
from django.db.models import Q
from django.http import Http404

class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтруем чаты, в которых участвует текущий пользователь
        return self.queryset.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Фильтруем группы, в которых участвует текущий пользователь"""
        return self.queryset.filter(members=self.request.user)
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from chat.models import Chat
from .serializers import ChatSerializer
from django.db.models import Q

class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтруем чаты, в которых участвует текущий пользователь
        return self.queryset.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        )

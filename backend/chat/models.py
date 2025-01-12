from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

class CustomUser (AbstractUser ):
    """Пользователь"""
    about = models.TextField()
    phone_number = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='images/', blank=True, null=True, default='images/user-default.png')

class Chat(models.Model):
    """Чат между пользователями"""
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chats_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chats_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Статус чата (активный/удаленный)

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"

class Message(models.Model):
    """Сообщение"""
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)  # Поле для статуса прочтения

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username if self.receiver else 'Unknown'} at {self.timestamp}"

class Group(models.Model):
    """Группа"""
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True, default='images/group-default.jpg')
    members = models.ManyToManyField(CustomUser , related_name='user_groups')
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания группы

    def __str__(self):
        return self.name
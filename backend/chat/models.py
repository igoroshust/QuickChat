from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

class CustomUser(AbstractUser):
    """Пользователь"""
    about = models.TextField()
    phone_number = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='images/', blank=True, null=True, default='images/user-default.png')

class Message(models.Model):
    """Сообщение"""
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.sender} to {self.receiver} at {self.timestamp}"

class Group(models.Model):
    """Группа"""
    name = models.CharField(max_length=255)
    image = models.URLField(blank=True, null=True)
    members = models.ManyToManyField(CustomUser)

    def __str__(self):
        return self.name

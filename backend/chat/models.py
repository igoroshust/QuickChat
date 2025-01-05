from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Пользователь"""
    about = models.TextField()
    phone_number = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='images/', blank=True, null=True)

class Test(models.Model):
    title = models.CharField(max_length=100)


# Generated by Django 5.1.4 on 2025-01-14 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_alter_message_chat'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='unread_count_user1',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='chat',
            name='unread_count_user2',
            field=models.IntegerField(default=0),
        ),
    ]

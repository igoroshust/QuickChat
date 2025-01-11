from rest_framework import serializers
from chat.models import Chat

class ChatSerializer(serializers.ModelSerializer):
    user1_avatar = serializers.ImageField(source='user1.photo', read_only=True)
    user2_avatar = serializers.ImageField(source='user2.photo', read_only=True)
    user1_username = serializers.CharField(source='user1.username', read_only=True)
    user2_username = serializers.CharField(source='user2.username', read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'user1_avatar', 'user2_avatar', 'user1_username', 'user2_username']
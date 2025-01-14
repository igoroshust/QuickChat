from rest_framework import serializers
from chat.models import Chat, Group

class ChatSerializer(serializers.ModelSerializer):
    user_avatar = serializers.ImageField(source='user2.photo', allow_null=True, read_only=True)
    user_username = serializers.CharField(source='user2.username', read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'user_avatar', 'user_username'] # только информация о user2

class GroupSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='name', read_only=True)
    group_image = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'group_name', 'group_image', 'members', 'created_at']
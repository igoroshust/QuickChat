from rest_framework import serializers
from chat.models import Chat, Group

class ChatSerializer(serializers.ModelSerializer):
    user1_avatar = serializers.ImageField(source='user1.photo', allow_null=True, read_only=True)
    user2_avatar = serializers.ImageField(source='user2.photo', allow_null=True, read_only=True)
    user1_username = serializers.CharField(source='user1.username', read_only=True)
    user2_username = serializers.CharField(source='user2.username', read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'user1_avatar', 'user2_avatar', 'user1_username', 'user2_username']

class GroupSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='name', read_only=True)
    group_image = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'group_name', 'group_image', 'members', 'created_at']
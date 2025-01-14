from rest_framework import serializers
from chat.models import Chat, Group, Message

class ChatSerializer(serializers.ModelSerializer):
    user_avatar = serializers.ImageField(source='user2.photo', allow_null=True, read_only=True)
    user_username = serializers.CharField(source='user2.username', read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'user_avatar', 'user_username', 'unread_count'] # только информация о user2

    def get_unread_count(self, obj):
        # Получаем текущего пользователя
        user = self.context['request'].user
        # Считаем непрочитанные сообщения для текущего пользователя
        return Message.objects.filter(chat=obj, receiver=user, is_read=False).count()

class GroupSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='name', read_only=True)
    group_image = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'group_name', 'group_image', 'members', 'created_at']
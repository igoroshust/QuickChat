from rest_framework import serializers
from chat.models import Chat, Group, Message

class ChatSerializer(serializers.ModelSerializer):
    """Сериализатор Чата"""
    user_avatar = serializers.ImageField(source='user2.photo', allow_null=True, read_only=True)
    user_username = serializers.CharField(source='user2.username', read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'user_avatar', 'user_username', 'unread_count'] # только информация о user2

    def get_unread_count(self, obj):
        """Непрочитанные сообщения"""
        user = self.context['request'].user # получаем текущего пользователя
        # Считаем непрочитанные сообщения для него
        return Message.objects.filter(chat=obj, receiver=user, is_read=False).count()

class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор Группы"""
    group_name = serializers.CharField(source='name', read_only=True)
    group_image = serializers.ImageField(source='image', read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'group_name', 'group_image', 'members', 'created_at', 'unread_count']

    def get_unread_count(self, obj):
        """Непрочитанные сообщения"""
        user = self.context['request'].user  # Получаем текущего пользователя
        # Подсчитываем непрочитанные сообщения для всех участников группы, кроме отправителя
        return Message.objects.filter(group=obj, is_read=False).exclude(sender=user).count()
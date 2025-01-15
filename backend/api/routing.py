from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/api/personal-chat/(?P<username>\w+)/$', consumers.PersonalChatConsumer.as_asgi()),  # Личный чат
    re_path(r'ws/api/group-chat/(?P<room_name>\w+)/$', consumers.GroupChatConsumer.as_asgi()),
]
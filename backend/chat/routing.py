from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/group-chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/personal-chat/(?P<username>\w+)/$', consumers.PersonalChatConsumer.as_asgi()),
]
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/api/chats/(?P<username>\w+)/$', consumers.PersonalChatConsumer.as_asgi()),  # personal-chat
    re_path(r'ws/api/groups/(?P<room_name>\w+)/$', consumers.GroupChatConsumer.as_asgi()), # group-chat
]
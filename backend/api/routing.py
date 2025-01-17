from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/api/chats/(?P<username>\w+)/$', consumers.ChatSideBarConsumer.as_asgi()),  # personal-chat
    re_path(r'ws/api/groups/(?P<room_name>\w+)/$', consumers.GroupSideBarConsumer.as_asgi()), # group-chat
]
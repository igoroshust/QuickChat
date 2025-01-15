from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from api.routing import websocket_urlpatterns as api_websocket_urlpatterns
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat_websocket_urlpatterns + api_websocket_urlpatterns  # Объединение маршрутов
        )
    ),
})

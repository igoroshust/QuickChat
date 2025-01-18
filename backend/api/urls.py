from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet, GroupViewSet, UpdateUnreadCountView

router = DefaultRouter()
router.register(r'chats', ChatViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('mark_messages_as_read/', UpdateUnreadCountView.as_view(), name='update_unread_count'),
]
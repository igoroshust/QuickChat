from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet, GroupViewSet, MarkMessagesAsReadView

router = DefaultRouter()
router.register(r'chats', ChatViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/mark_messages_as_read/', MarkMessagesAsReadView.as_view(), name='mark_messages_as_read'),
]
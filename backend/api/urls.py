from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet, GroupViewSet

router = DefaultRouter()
router.register(r'chats', ChatViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
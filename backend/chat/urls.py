from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index, name="home"),
    path('login/', login, name="login"),
    path('signup/', signup, name="signup"),
    path('empty-main/', empty_main, name="empty_main"),
]

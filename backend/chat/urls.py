from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index, name="home"),
    path('login/', login_view, name="login"),
    path('signup/', signup, name="signup"),
    path('empty-main/', empty_main, name="empty_main"),
    path('main/', main, name="main"),
    path('user-list/', user_list, name="user_list"),
    path('user-profile/', user_profile, name="user_profile"),
    path('edit-profile/', edit_profile, name="edit_profile"),
    path('create-group/', create_group, name="create_group"),
    path('personal-chat/', personal_chat, name="personal_chat"),
    path('group-chat/', group_chat, name="group_chat"),
    path('add-members/', add_members, name="add_members"),
    path('update-group/', update_group, name="update_group"),
    path('delete-group/', delete_group, name="delete_group"),
    path('delete-chat/', delete_chat, name="delete_chat"),

    path('sidebar/', sidebar, name="sidebar"),
]

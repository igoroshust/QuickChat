from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="home"),
    path('login/', login_view, name="login"),
    path('signup/', signup, name="signup"),
    path('empty-main/', empty_main, name="empty_main"),
    path('main/', main, name="main"),
    path('user-list/', user_list, name="user_list"),
    path('user-profile/<str:user>/', user_profile, name="user_profile"),
    path('edit-profile/', UserProfileUpdateView.as_view(), name="edit_profile"), # edit_profile
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('create-group/', GroupCreateView.as_view(), name='create_group'),
    path('edit-group/<int:pk>/', GroupUpdateView.as_view(), name='edit_group'),
    path('delete-group/<int:pk>/', GroupDeleteView.as_view(), name='delete_group'),
    path('group-chat/<int:group_id>/', group_chat_view, name='group_chat_view'),
    path('personal-chat/<str:user>/', chat_view, name="personal_chat"),
    path('delete-chat/<str:user>/', ChatDeleteView.as_view(), name='delete_chat'),
    path('add-members/<int:group_id>', add_members, name="add_members"),
    path('update-group/', update_group, name="update_group"),
    path('delete-group/', delete_group, name="delete_group"),
    path('sidebar/', sidebar, name="sidebar"),
    # path('send_message/', send_message, name='send_message'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
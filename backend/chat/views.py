from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomSignupForm
from .models import CustomUser, Message
from django.db.models import Q


def index(request):
    return render(request, '../templates/home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            return render(request, 'chat/login.html', {'error': 'Неверный логин или пароль'})
    return render(request, 'chat/login.html')


def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('main')
    else:
        form = CustomSignupForm()
    return render(request, 'chat/signup.html', {'form': form})


def main(request):
    return render(request, '../templates/chat/main.html')


def sidebar(request):
    return render(request, '../templates/chat/components/sidebar.html')


def empty_main(request):
    return render(request, '../templates/chat/empty-main.html')

@login_required
def user_list(request):
    users = CustomUser.objects.exclude(username=request.user.username)
    return render(request, '../templates/chat/user-list.html', {'users': users})


def user_profile(request):
    return render(request, '../templates/chat/user-profile.html')


def create_group(request):
    return render(request, '../templates/chat/create-group.html')


@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_username = request.POST['receiver']
        content = request.POST['content']
        receiver = get_object_or_404(CustomUser, username=receiver_username)
        Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return redirect('personal_chat', user=receiver_username)  # Перенаправление на чат с получателем


@login_required
def chat_view(request, user):
    other_user = get_object_or_404(CustomUser, username=user)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    return render(request, 'chat/chat.html', {
        'messages': messages,
        'other_user': other_user,
        'chat_type': 'personal',  # Указываем тип чата
        'chat_avatar_url': other_user.photo,  # Замените на правильный URL аватара
        'chat_title': other_user.username  # Имя пользователя
    })


@login_required
def group_chat_view(request, group_id):
    # Здесь вы можете реализовать логику для группового чата
    # Например, получить сообщения группы и передать их в шаблон
    messages = []  # Замените на вашу логику получения сообщений группы
    return render(request, 'chat/chat.html', {
        'messages': messages,
        'chat_title': 'Название группы',  # Замените на название группы
        'chat_avatar_url': 'URL_аватара_группы',  # Замените на URL аватара группы
        'chat_type': 'group'  # Указываем тип чата
    })


def add_members(request):
    return render(request, '../templates/chat/actions/add-members.html')


def update_group(request):
    return render(request, '../templates/chat/actions/update-group.html')


def delete_group(request):
    return render(request, '../templates/chat/actions/delete-group.html')


def delete_chat(request):
    return render(request, '../templates/chat/actions/delete-chat.html')


def edit_profile(request):
    return render(request, '../templates/chat/edit-profile.html')

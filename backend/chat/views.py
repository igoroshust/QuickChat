from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView, CreateView, DeleteView
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomSignupForm, UserProfileForm, GroupForm
from .models import CustomUser, Message, Group, Chat
from django.db.models import Q
from django.http import Http404
import logging

logger = logging.getLogger(__name__)

def index(request):
    """Приветственная страница для неавторизованного пользователя"""
    return render(request, '../templates/home.html')


def login_view(request):
    """Авторизация"""
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
    """Регистрация"""
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('main')
    else:
        form = CustomSignupForm()
    return render(request, 'chat/signup.html', {'form': form})


def main(request):
    """Главная страница внутри приложения"""
    return render(request, '../templates/chat/main.html')


def sidebar(request):
    """Сайдбар"""
    return render(request, '../templates/chat/components/sidebar.html')


@login_required
def user_list(request):
    """Список пользователей"""
    users = CustomUser.objects.exclude(username=request.user.username)
    return render(request, '../templates/chat/user-list.html', {'users': users})

@login_required
def user_profile(request, user):
    """Профиль пользователя"""
    user_object = get_object_or_404(CustomUser , username=user)
    return render(request, '../templates/chat/user-profile.html', {
        'user': request.user,  # Передаем текущего пользователя
        'profile_user': user_object  # Передаем пользователя профиля
    })

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""
    model = CustomUser
    form_class = UserProfileForm
    template_name = '../templates/chat/edit-profile.html'
    success_url = reverse_lazy('main')

    def get_object(self, queryset=None):
        return self.request.user # Возвращаем только аутентифицированного пользователя

    def form_valid(self, form):
        """Обработка загрузки аватара"""
        if self.request.FILES.get('photo'):
            form.instance.photo = self.request.FILES['photo']
        return super().form_valid(form) # Сохраняем форму


@login_required
def chat_view(request, user):
    """Личная переписка"""
    other_user = get_object_or_404(CustomUser , username=user)

    # Обновляем статус всех непрочитанных сообщений
    Message.objects.filter(receiver=request.user, sender=other_user, is_read=False).update(is_read=True)

    # Получаем все сообщения между текущим пользователем и другим пользователем
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    # Получаем количество непрочитанных сообщений для отображения (если нужно)
    unread_count = Message.objects.filter(receiver=request.user, sender=other_user, is_read=False).count()

    return render(request, 'chat/chat.html', {
        'messages': messages,
        'other_user': other_user,
        'chat_type': 'personal',  # Указываем тип чата
        'chat_avatar_url': other_user.photo.url if other_user.photo else None,  # URL аватара
        'chat_title': other_user.username,  # Имя пользователя
        'unread_count': unread_count,  # Количество непрочитанных сообщений
    })

class ChatDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление личной переписки"""
    model = Chat
    template_name = '../templates/chat/actions/delete-chat.html'  # Шаблон для подтверждения удаления
    success_url = reverse_lazy('main')  # URL для перенаправления после успешного удаления

    def get_object(self, queryset=None):
        """Получаем объект для удаления"""
        other_user_username = self.kwargs['user']
        other_user = get_object_or_404(CustomUser , username=other_user_username)

        # Ищем чат, где текущий пользователь является user1 или user2
        chat = Chat.objects.filter(
            Q(user1=self.request.user, user2=other_user) |
            Q(user1=other_user, user2=self.request.user)
        ).first()  # Получаем первый найденный чат или None

        if chat is None:
            raise Http404("Chat does not exist")  # Если чат не найден, выбрасываем 404

        return chat

    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста в шаблон"""
        context = super().get_context_data(**kwargs)
        context['other_user'] = self.get_object().user2 if self.get_object().user1 == self.request.user else self.get_object().user1
        return context

    def delete(self, request, *args, **kwargs):
        chat = self.get_object()
        # Удаляем все сообщения, связанные с чатом
        messages = Message.objects.filter(chat=chat)
        messages_count = messages.count()  # Считаем количество сообщений для отладки
        messages.delete()  # Удаляем все сообщения, связанные с этим чатом

        # Отправка обновления в сайдбар
        chat_data = {
            'chat_id': chat.id,
        }
        # Отправляем обновление в группу сайдбара
        async_to_sync(channel_layer.group_send)(
            f'api_chat_sidebar_{chat.user1.username}',
            {
                'type': 'chat_deleted',
                'chat_data': chat_data,
            }
        )
        async_to_sync(channel_layer.group_send)(
            f'api_chat_sidebar_{chat.user2.username}',
            {
                'type': 'chat_deleted',
                'chat_data': chat_data,
            }
        )

        logger.info(f"Deleted {messages_count} messages from chat between {chat.user1.username} and {chat.user2.username}.")  # Логируем удаление
        return super().delete(request, *args, **kwargs)  # Удаляем сам чат

@login_required
def group_chat_view(request, group_id):
    """Групповой чат"""
    group = get_object_or_404(Group, id=group_id)

    # Обновляем статус всех непрочитанных сообщений для текущего пользователя
    Message.objects.filter(group=group, is_read=False).exclude(sender=request.user).update(is_read=True)

    # Получаем сообщения, связанные с этой группой, и сортируем их по времени
    messages = Message.objects.filter(group=group).order_by('timestamp')

    # Подсчитываем количество непрочитанных сообщений для текущего пользователя в этой группе
    unread_count = Message.objects.filter(group=group, is_read=False).exclude(sender=request.user).count()

    return render(request, 'chat/chat.html', {
        'messages': messages,
        'chat_title': group.name,
        'chat_avatar_url': group.image.url if group.image else None,
        'chat_type': 'group',
        'group': group,
        'unread_count': unread_count
    })


@login_required
def add_members(request, group_id):
    """Добавление участника в группу"""
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        members = request.POST.get('members', '').split(',')  # Разделяем участников по запятой

        # Добавляем участников в группу
        for member in members:
            member = member.strip()
            try:
                user = CustomUser .objects.get(username=member)
                if not group.members.filter(id=user.id).exists():
                    group.members.add(user)
                    logger.info(f'Пользователь "{user.username}" добавлен в группу "{group.name}".')
                else:
                    logger.warning(f'Пользователь "{user.username}" уже является участником группы "{group.name}".')
            except CustomUser .DoesNotExist:
                logger.error(f'Пользователь с именем "{member}" не найден.')

        # Перенаправляем на страницу чата группы
        return redirect('group_chat_view', group_id=group.id)

    return render(request, '../templates/chat/actions/add-members.html', {'group': group})

class GroupCreateView(LoginRequiredMixin, CreateView):
    """Создание группы"""
    model = Group
    form_class = GroupForm
    template_name = '../templates/chat/create-group.html'
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        group = form.save(commit=False)
        group.save()

        # Добавляем создателя группы в участники
        group.members.add(self.request.user)

        # Получаем участников из формы
        members = self.request.POST.get('members', '').split(',')
        for member in members:
            member = member.strip()
            try:
                user = CustomUser.objects.get(username=member)
                group.members.add(user)

            except CustomUser.DoesNotExist:
                form.add_error('members', f'Пользователь с именем "{member}" не найден.')
                # Перенаправляем на страницу чата группы

        # Отправка обновления в сайдбар
        group_data = {
            'id': group.id,
            'group_name': group.name,
            'group_image': group.image.url if group.image else None,
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'api_group_sidebar_{self.request.user.username}',  # Уникальная группа для сайдбара
            {
                'type': 'group_created',
                'group_data': group_data,
            }
        )

        return redirect('group_chat_view', group_id=group.id)  # Здесь мы перенаправляем на страницу чата группы

class GroupUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление группы"""
    model = Group
    form_class = GroupForm
    template_name = '../templates/chat/actions/update-group.html'

    def get_object(self, queryset=None):
        """Получаем группу по ID"""
        return get_object_or_404(Group, id=self.kwargs['pk'])

    def form_valid(self, form):
        group = form.save(commit=False)  # Сохраняем изменения в группе, но не в БД
        group.save()  # Сохраняем группу в БД

        # Обработка участников
        members = self.request.POST.get('members', '').split(',')  # Получаем участников из формы
        group.members.clear()  # Удаляем всех текущих участников

        for member in members:
            member = member.strip()
            try:
                user = CustomUser .objects.get(username=member)
                group.members.add(user)  # Добавляем нового участника
            except CustomUser .DoesNotExist:
                form.add_error('members', f'Пользователь с именем "{member}" не найден.')

        return super().form_valid(form)  # Перенаправляем на success_url

    def get_success_url(self):
        """Возвращаем URL для перенаправления после успешного редактирования"""
        return reverse_lazy('group_chat_view', kwargs={'group_id': self.object.id})

class GroupDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление группы"""
    model = Group
    template_name = '../templates/chat/actions/delete-group.html'
    success_url = reverse_lazy('main')  # Перенаправление после успешного удаления

    def get_object(self, queryset=None):
        """Получаем объект для удаления"""
        return get_object_or_404(Group, id=self.kwargs['pk'])  # Получаем группу по ID

    def delete(self, request, *args, **kwargs):
        group = self.get_object()
        # Удаляем все сообщения, связанные с группой
        messages = Message.objects.filter(group=group)
        messages.delete()  # Удаляем все сообщения, связанные с этой группой

        # Отправка обновления в сайдбар
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'api_group_sidebar_{self.request.user.username}',  # Уникальная группа для сайдбара
            {
                'type': 'group_deleted',
                'group_id': group.id,
            }
        )

        return super().delete(request, *args, **kwargs)  # Удаляем саму группу



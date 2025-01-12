import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomSignupForm, UserProfileForm, GroupForm
from .models import CustomUser, Message, Group, Chat
from django.db.models import Q

logger = logging.getLogger(__name__)

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

@login_required
def user_profile(request, user):
    user_object = get_object_or_404(CustomUser , username=user)
    return render(request, '../templates/chat/user-profile.html', {
        'user': request.user,  # Передаем текущего пользователя
        'profile_user': user_object  # Передаем пользователя профиля
    })

@login_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST['group_name']
        group_avatar = request.POST.get('group_avatar', '')
        members = request.POST['members'].split(',')  # Разделяем участников по запятой

        # Создаём группу
        group = Group.objects.create(name=group_name, image=group_avatar)

        # Добавляем участников в группу
        for member in members:
            user = get_object_or_404(CustomUser , username=member.strip())
            group.members.add(user)
            logger.info(f'Пользователь "{user.username}" добавлен в группу "{group.name}".')

        # Перенаправляем на страницу чата группы
        return redirect('group_chat_view', group_id=group.id)

    return render(request, '../templates/chat/create-group.html')

@login_required
def group_chat_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    messages = Message.objects.filter(group=group).order_by('timestamp')

    return render(request, 'chat/chat.html', {
        'messages': messages,
        'chat_title': group.name,
        'chat_avatar_url': group.image if group.image else None,
        'chat_type': 'group',
        'group': group
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message, Chat, CustomUser , Group

@login_required
def send_message(request):
    if request.method == 'POST':
        content = request.POST['content']
        group_id = request.POST.get('group_id')  # Получите ID группы из формы
        receiver_username = request.POST.get('receiver')  # Получаем имя получателя, если это личный чат

        if group_id:  # Если ID группы присутствует, значит, это групповой чат
            group = get_object_or_404(Group, id=group_id)
            # Создайте сообщение с указанием группы
            message = Message.objects.create(sender=request.user, content=content, group=group)
            return redirect('group_chat_view', group_id=group.id)  # Перенаправление на групповой чат
        elif receiver_username:  # Если это личный чат
            receiver = get_object_or_404(CustomUser , username=receiver_username)
            # Получаем или создаем чат между пользователями
            chat, created = Chat.objects.get_or_create(user1=request.user, user2=receiver)

            # Проверяем, что чат был успешно получен или создан
            if chat:
                # Создайте сообщение с указанием чата
                message = Message.objects.create(sender=request.user, receiver=receiver, content=content, chat=chat)
                return redirect('personal_chat', user=receiver_username)  # Перенаправление на личный чат
            else:
                # Обработка случая, когда чат не был создан
                return redirect('main')  # Или обработайте ошибку
        else:
            return redirect('main')  # Если ни то, ни другое, перенаправляем на главную страницу

    return redirect('main')  # Если метод не POST, перенаправляем на главную страницу

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
def add_members(request, group_id):
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


def update_group(request):
    return render(request, '../templates/chat/actions/update-group.html')


def delete_group(request):
    return render(request, '../templates/chat/actions/delete-group.html')

@login_required
def delete_chat(request, user):
    return render(request, '../templates/chat/actions/delete-chat.html', {'user': user})


@login_required
def edit_profile(request):
    user_object = request.user

    if request.method == 'POST':
        user_object.username = request.POST.get('username', user_object.username)
        user_object.about = request.POST.get('about', user_object.about)

        # Обработка загрузки аватара
        if request.FILES.get('avatar'):
            user_object.photo = request.FILES['avatar']

        user_object.save()
        return redirect('main')

    return render(request, '../templates/chat/edit-profile.html', {'user': user_object})

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
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


class GroupCreateView(LoginRequiredMixin, CreateView):
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

        return redirect('group_chat_view', group_id=group.id)  # Здесь мы перенаправляем на страницу чата группы

class GroupUpdateView(LoginRequiredMixin, UpdateView):
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
    model = Group
    template_name = '../templates/chat/actions/delete-group.html'
    success_url = reverse_lazy('main')  # Перенаправление после успешного удаления

    def get_object(self, queryset=None):
        return get_object_or_404(Group, id=self.kwargs['pk'])  # Получаем группу по ID

class ChatDeleteView(LoginRequiredMixin, DeleteView):
    model = Chat
    template_name = '../templates/chat/actions/delete-chat.html'  # Шаблон для подтверждения удаления
    success_url = reverse_lazy('main')  # URL для перенаправления после успешного удаления

    def get_object(self, queryset=None):
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
        context = super().get_context_data(**kwargs)
        context['other_user'] = self.get_object().user2 if self.get_object().user1 == self.request.user else self.get_object().user1
        return context

    def delete(self, request, *args, **kwargs):
        chat = self.get_object()
        # Удаляем все сообщения, связанные с чатом
        messages = Message.objects.filter(chat=chat)
        messages_count = messages.count()  # Считаем количество сообщений для отладки
        messages.delete()  # Удаляем все сообщения, связанные с этим чатом
        logger.info(f"Deleted {messages_count} messages from chat between {chat.user1.username} and {chat.user2.username}.")  # Логируем удаление
        return super().delete(request, *args, **kwargs)  # Удаляем сам чат
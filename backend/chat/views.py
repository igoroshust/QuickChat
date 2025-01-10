from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomSignupForm, UserProfileForm, GroupForm
from .models import CustomUser, Message, Group
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

@login_required
def user_profile(request, user):
    user_object = get_object_or_404(CustomUser , username=user)
    return render(request, '../templates/chat/user-profile.html', {'user': user_object})

@login_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST['group_name']
        group_avatar = request.POST.get('group_avatar', '')
        members = request.POST['members'].split(',') # разделяем участников по запятой

        # Создаём группу
        group = Group.objects.create(name=group_name, image=group_avatar)

        # Добавляем участников в группу
        for member in members:
            user = get_object_or_404(CustomUser, username=member.strip())
            group.members.add(user)

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

@login_required
def send_message(request):
    if request.method == 'POST':
        content = request.POST['content']
        group_id = request.POST.get('group_id')  # Получите ID группы из формы
        receiver_username = request.POST.get('receiver')  # Получаем имя получателя, если это личный чат

        if group_id:  # Если ID группы присутствует, значит, это групповой чат
            group = get_object_or_404(Group, id=group_id)
            Message.objects.create(sender=request.user, content=content, group=group)  # Создайте сообщение с указанием группы
            return redirect('group_chat_view', group_id=group.id)  # Перенаправление на групповой чат
        elif receiver_username:  # Если это личный чат
            receiver = get_object_or_404(CustomUser , username=receiver_username)
            Message.objects.create(sender=request.user, receiver=receiver, content=content)  # Создайте сообщение с указанием получателя
            return redirect('personal_chat', user=receiver_username)  # Перенаправление на личный чат
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

def add_members(request):
    return render(request, '../templates/chat/actions/add-members.html')


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
        members = self.request.POST.get('members', '').split(',')
        for member in members:
            member = member.strip()
            try:
                user = CustomUser .objects.get(username=member)
                group.members.add(user)
            except CustomUser .DoesNotExist:
                form.add_error('members', f'Пользователь с именем "{member}" не найден.')
                # Перенаправляем на страницу чата группы

        return redirect('group_chat_view', group_id=group.id)  # Здесь мы перенаправляем на страницу чата группы

class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = '../templates/chat/actions/update-group.html'
    success_url = reverse_lazy('main')  # Перенаправление после успешного редактирования

    def get_object(self, queryset=None):
        return get_object_or_404(Group, id=self.kwargs['pk'])  # Получаем группу по ID

class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = '../templates/chat/action/delete-group.html'
    success_url = reverse_lazy('main')  # Перенаправление после успешного удаления

    def get_object(self, queryset=None):
        return get_object_or_404(Group, id=self.kwargs['pk'])  # Получаем группу по ID
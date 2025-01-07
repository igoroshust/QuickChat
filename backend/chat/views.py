from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from allauth.account.views import SignupView
from .forms import CustomSignupForm

def index(request):
    return render(request, '../templates/home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Замените 'home' на нужный вам URL
        else:
            # Обработка ошибки входа
            return render(request, 'chat/login.html', {'error': 'Неверный логин или пароль'})
    return render(request, 'chat/login.html')

def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save(request)  # Сохраняем пользователя
            return redirect('home')  # Замените 'home' на нужный вам URL
    else:
        form = CustomSignupForm()

    return render(request, 'chat/signup.html', {'form': form})

def empty_main(request):
    return render(request, '../templates/chat/empty-main.html')

def user_list(request):
    return render(request, '../templates/chat/user-list.html')

def user_profile(request):
    return render(request, '../templates/chat/user-profile.html')

def create_group(request):
    return render(request, '../templates/chat/create-group.html')

def empty_chat(request):
    return render(request, '../templates/chat/empty-chat.html')

def empty_group(request):
    return render(request, '../templates/chat/empty-group.html')

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
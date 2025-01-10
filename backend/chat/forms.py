from allauth.account.forms import SignupForm
from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django import forms
from .models import *

class CustomSignupForm(SignupForm):
    """Кастомная форма регистрации"""
    username = forms.CharField(max_length=30, label='Логин')
    email = forms.EmailField(label='Почта')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    def signup(self, request, user):
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend') # Вход в систему после регистрации
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'about', 'photo']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg'}),
            'about': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg', 'rows': 4}),
            'photo': forms.FileInput(attrs={'class': 'hidden'}),  # Скрываем стандартный виджет
        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields =['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'image': forms.FileInput(attrs={'class': 'hidden'}),
        }
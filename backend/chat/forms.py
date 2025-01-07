from allauth.account.forms import SignupForm
from django import forms

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
        return user
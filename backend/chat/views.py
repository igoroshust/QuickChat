from django.shortcuts import render

def index(request):
    return render(request, '../templates/index.html')

def login(request):
    return render(request, '../templates/chat/login.html')

def signup(request):
    return render(request, '../templates/chat/signup.html')

def empty_main(request):
    return render(request, '../templates/chat/empty-main.html')
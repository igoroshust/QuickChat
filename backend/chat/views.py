from django.shortcuts import render

def index(request):
    return render(request, '../templates/index.html')

def login(request):
    return render(request, '../templates/chat/login.html')

def signup(request):
    return render(request, '../templates/chat/signup.html')

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
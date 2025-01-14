from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Message)
admin.site.register(Group)
admin.site.register(Chat)

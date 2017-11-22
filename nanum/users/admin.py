from django.contrib import admin
from django.conf import settings
# Register your models here.

from .models import User

admin.site.register(User)
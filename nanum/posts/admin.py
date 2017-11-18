from django.contrib import admin
from .models import answer, question, images

admin.site.register(answer)
admin.site.register(question)
admin.site.register(images)
from django.contrib import admin

from .models import Images, Question, Answer

admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(Images)

from django.contrib import admin

from .models import Question, Answer

admin.site.register(Answer)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'modified_at']

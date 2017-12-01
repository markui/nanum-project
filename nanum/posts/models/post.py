from django.conf import settings
from django.db import models

from . import PostManager

__all__ = (
    'Question',
    'Answer',
)


# user가 None이면 쿼리에서 제외
class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(user=None)


class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=150)
    topic = models.ForeignKey('topics.Topic', related_name='questions')
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    objects = QuestionManager()

    def save(self, *args, **kwargs):
        super().save()
        PostManager.objects.create(question=self)

    def __str__(self):
        return f'user: {self.user}, content: {self.content}'


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save()
        PostManager.objects.create(answer=self)

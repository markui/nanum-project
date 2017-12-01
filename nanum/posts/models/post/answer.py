from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from ...models import PostManager

__all__ = (
    'Answer',
    'AnswerContent',
)


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save()
        post_manager = PostManager.objects.get_or_create(answer=self)

class AnswerContent(models.Model):
    text = models.TextField()
    image = models.ImageField()
    answer = models.ForeignKey(
        'Answer',
        on_delete=models.CASCADE,
    )

from django.db import models
from django.conf import settings

__all__ = (
    'Question',
)


# user가 None이면 쿼리에서 제외
class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(user=None)


class Question(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    objects = QuestionManager()



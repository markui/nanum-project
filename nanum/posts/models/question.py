from django.db import models

from topics.models import Topic
from users.models import User

__all__ = (
    'Question',
)


# user가 None이면 쿼리에서 제외
class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(user=None)


class Question(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
    )
    title = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)

    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
    )

    objects = QuestionManager()



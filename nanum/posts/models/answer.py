from django.db import models

from users.models import User
from . import Question

__all__ = (
    'Answer',
)


class Answer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
    )
    content = models.TextField()
    created_at = models.DateField(auto_now_add=True)




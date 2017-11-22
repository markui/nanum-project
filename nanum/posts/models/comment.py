from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from posts.models.answer import Answer
from posts.models.question import Question

User = settings.AUTH_USER_MODEL

class Comment(models.Model):
    """
    Question과 Answer Comment를 위한 Abstract Model
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    comment = models.TextField(
        max_length=2000,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    modified = models.DateTimeField(
        auto_now=True,
    )
    nested_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
    )
    # like = models.ManyToManyField(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='comments'
    # )

    class Meta:
        abstract = True

class QuestionComment(Comment):
    """

    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='comments'
    )

class AnswerComment(Comment):
    """

    """
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='comments'
    )

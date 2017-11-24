from django.conf import settings
from django.db import models


__all__ =(
    'QuestionComment',
    'AnswerComment',
    'NestedComment',
)


class Comment(models.Model):
    """
    Question과 Answer Comment를 위한 Abstract Model
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    content = models.TextField(
        max_length=2000,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    modified_at = models.DateTimeField(
        auto_now=True,
    )

    # like = models.ManyToManyField(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='comments'
    # )

    def __str__(self):
        return f'{self.user} - {self.comment[:50]}'

    class Meta:
        abstract = True


class QuestionComment(Comment):
    """
    질문에 대한 댓글
    """
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='comments'
    )


class AnswerComment(Comment):
    """
    답변에 대한 댓글
    """
    answer = models.ForeignKey(
        'Answer',
        on_delete=models.CASCADE,
        related_name='comments'
    )


class NestedComment(Comment):
    """
    댓글에 대한 댓글
    """
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
    )

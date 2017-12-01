from django.conf import settings
from django.db import models

__all__ = (
    'QuestionBookmarkRelation',
    'AnswerBookmarkRelation',
)


class QuestionBookmarkRelation(models.Model):
    """
    질문 북마크
    """
    # 북마크 하는 유저(from)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # 북마크 받은 질문(to)
    question = models.ForeignKey('posts.Question', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')


# 답변 북마크
class AnswerBookmarkRelation(models.Model):
    """
    답변 북마크
    """
    # 북마크 하는 유저(from)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # 북마크 받은 답변(to)
    answer = models.ForeignKey('posts.Answer', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')

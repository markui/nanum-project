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

    def save(self, *args, **kwargs):
        super().save()
        if self.question.bookmark_count < 0:
            self.question.bookmark_count = 1
        else:
            self.question.bookmark_count += 1
        self.question.save()

    def delete(self, *args, **kwargs):
        super().delete()
        if self.question.bookmark_count > 0:
            self.question.bookmark_count -= 1
        else:
            self.question.bookmark_count = 0
        self.question.save()


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

    def save(self, *args, **kwargs):
        super().save(self, *args, **kwargs)
        if self.answer.bookmark_count < 0:
            self.answer.bookmark_count = 1
        else:
            self.answer.bookmark_count += 1
        self.answer.save()

    def delete(self, *args, **kwargs):
        super().delete(self, *args, **kwargs)
        if self.answer.bookmark_count > 0:
            self.answer.bookmark_count -= 1
        else:
            self.answer.bookmark_count = 0
        self.answer.save()

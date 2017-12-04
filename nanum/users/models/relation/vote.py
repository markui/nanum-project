from django.conf import settings
from django.db import models

__all__ = (
    # 답변
    'BaseAnswerVoteRelation',
    'AnswerUpVoteRelation',
    'AnswerDownVoteRelation',

    # 코멘트
    'BaseCommentVoteRelation',
    'CommentUpVoteRelation',
    'CommentDownVoteRelation',
)


# 답변 추천/비추천
class BaseAnswerVoteRelation(models.Model):
    """
    상속받는 기본 추천/비추천 모델
    """
    # 투표 하는 유저(from)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # 투표 받은 답변(to)
    answer = models.ForeignKey('posts.Answer', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AnswerUpVoteRelation(BaseAnswerVoteRelation):
    """
    답변 추천
    """

    class Meta:
        unique_together = ('user', 'answer')

    def save(self, *args, **kwargs):
        super().save(self, *args, **kwargs)
        self.answer.upvote_count += 1
        self.answer.save()

    def delete(self, *args, **kwargs):
        super().delete(self, *args, **kwargs)
        self.answer.upvote_count -= 1
        self.answer.save()


class AnswerDownVoteRelation(BaseAnswerVoteRelation):
    """
    답변 비추천
    """

    class Meta:
        unique_together = ('user', 'answer')

    def save(self, *args, **kwargs):
        super().save(self, *args, **kwargs)
        self.answer.downvote_count += 1
        if self.answer.upvote_count > 0:
            self.answer.upvote_count -= 1
        self.answer.save()

    def delete(self, *args, **kwargs):
        super().delete(self, *args, **kwargs)
        self.answer.downvote_count -= 1
        self.answer.save()


# 댓글 추천/비추천
# 기본 댓글 관계
class BaseCommentVoteRelation(models.Model):
    """
    상속받는 기본 추천/비추천 모델
    """
    # 투표 하는 유저(from)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey('posts.Comment', on_delete=models.CASCADE)

    class Meta:
        abstract = True


class CommentUpVoteRelation(BaseCommentVoteRelation):
    class Meta:
        unique_together = ('user', 'comment')

    def save(self, *args, **kwargs):
        super().save(self, *args, **kwargs)
        self.comment.upvote_count += 1
        self.comment.save()

    def delete(self, *args, **kwargs):
        super().delete(self, *args, **kwargs)
        self.comment.upvote_count -= 1
        self.comment.save()


class CommentDownVoteRelation(BaseCommentVoteRelation):
    class Meta:
        unique_together = ('user', 'comment')

    def save(self, *args, **kwargs):
        super().save(self, *args, **kwargs)
        self.comment.downvote_count += 1
        if self.comment.upvote_count > 0:
            self.comment.upvote_count -= 1
        self.comment.save()

    def delete(self, *args, **kwargs):
        super().delete(self, *args, **kwargs)
        self.comment.downvote_count -= 1
        self.comment.save()

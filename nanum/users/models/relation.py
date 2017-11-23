from django.conf import settings
from django.db import models


class UserFollow(models.Model):
    """
    유저 팔로우
    """
    # 팔로우 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following_relations',
    )
    # 팔로우 받는 유저(to)
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower_relations',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'target')


class TopicFollow(models.Model):
    """
    주제 팔로우
    """
    # 팔로우 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 팔로우 받는 주제(to)
    topic = models.ForeignKey(
        'topics.Topic',
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TopicExpertiseFollow(TopicFollow):
    class Meta:
        unique_together = ('user', 'topic')


class TopicInterestFollow(TopicFollow):
    class Meta:
        unique_together = ('user', 'topic')


class QuestionFollow(models.Model):
    """
    질문 팔로우
    """

    # 팔로우 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 팔로우 받는 질문(to)
    question = models.ForeignKey(
        'posts.Question',
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')


class QuestionBookmark(models.Model):
    """
    질문 북마크
    """
    # 북마크 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 북마크 받은 질문(to)
    question = models.ForeignKey(
        'posts.Question',
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')


# 답변 추천/비추천
class BaseAnswerVote(models.Model):
    """
    상속받는 기본 추천/비추천 모델
    """
    # 투표 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 투표 받은 답변(to)
    answer = models.ForeignKey(
        'posts.Answer',
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AnswerUpVote(BaseAnswerVote):
    """
    답변 추천
    """

    class Meta:
        unique_together = ('user', 'answer')


class AnswerDownVote(BaseAnswerVote):
    """
    답변 비추천
    """

    class Meta:
        unique_together = ('user', 'answer')


# 답변 북마크
class AnswerBookmark(models.Model):
    """
    답변 북마크
    """
    # 북마크 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 북마크 받은 답변(to)
    answer = models.ForeignKey(
        'posts.Answer',
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')


# 댓글 추천/비추천
# 기본 댓글 관계
class BaseCommentVote(models.Model):
    """
    상속받는 기본 추천/비추천 모델
    """
    # 투표 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


# 댓글 종류별(질문-댓글/답변-댓글/댓글-댓글) 댓글 관계
class BaseQuestionCommentVote(BaseCommentVote):
    # 투표 받은 댓글(to)
    comment = models.ForeignKey(
        'posts.QuestionComment',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('user', 'comment')


class BaseAnswerCommentVote(BaseCommentVote):
    # 투표 받은 댓글(to)
    comment = models.ForeignKey(
        'posts.AnswerComment',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('user', 'comment')


class BaseNestedCommentVote(BaseCommentVote):
    # 투표 받은 댓글(to)
    comment = models.ForeignKey(
        'posts.NestedComment',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('user', 'comment')


# 댓글 종류별 추천/비추천

class QuestionCommentUpVote(BaseQuestionCommentVote):
    """
    질문-댓글 추천
    """
    pass


class QuestionCommentDownVote(BaseQuestionCommentVote):
    """
    질문-댓글 비추천
    """
    pass


class AnswerCommentUpVote(BaseAnswerCommentVote):
    """
    답변-댓글 추천
    """
    pass


class AnswerCommentDownVote(BaseAnswerCommentVote):
    """
    답변-댓글 비추천
    """
    pass


class NestedCommentUpVote(BaseNestedCommentVote):
    """
    댓글-댓글 추천
    """
    pass


class NestedCommentDownVote(BaseNestedCommentVote):
    """
    댓글-댓글 비추천
    """
    pass

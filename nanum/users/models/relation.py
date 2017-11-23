from django.conf import settings
from django.db import models


class FollowUser(models.Model):
    """
    유저 팔로우
    """
    # 팔로우 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follow_user_relations',
    )
    # 팔로우 받는 유저(to)
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follow_user_relations',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'target')


class FollowTopic(models.Model):
    """
    주제 팔로우
    """
    # 팔로우 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follow_topic_relations',
    )
    # 팔로우 받는 주제(to)
    target = models.ForeignKey(
        'topics.Topic',
        on_delete=models.CASCADE,
        related_name='follow_topic_relations',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'target')


class FollowQuestion(models.Model):
    """
    질문 팔로우
    """

    # 팔로우 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follow_question_relations',
    )
    # 팔로우 받는 질문(to)
    target = models.ForeignKey(
        'posts.Question',
        on_delete=models.CASCADE,
        related_name='follow_question_relations',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'target')


class BookmarkQuestion(models.Model):
    """
    질문 북마크
    """
    # 북마크 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmark_question_relations',
    )
    # 북마크 받은 질문(to)
    target = models.ForeignKey(
        'posts.Question',
        on_delete=models.CASCADE,
        related_name='bookmark_question_relations',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'target')


# 답변 추천/비추천
class BaseVoteAnswer(models.Model):
    """
    상속받는 기본 추천/비추천 모델
    """
    # 투표 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 투표 받은 답변(to)
    target = models.ForeignKey(
        'posts.Answer',
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'target')


class UpVoteAnswer(BaseVoteAnswer):
    """
    답변 추천
    """
    pass


class DownVoteAnswer(BaseVoteAnswer):
    """
    답변 비추천
    """
    pass


# 답변 북마크
class BookmarkAnswer(models.Model):
    """
    답변 북마크
    """
    # 북마크 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmark_answer_relations',
    )
    # 북마크 받은 답변(to)
    target = models.ForeignKey(
        'posts.Answers',
        on_delete=models.CASCADE,
        related_name='bookmark_answer_relations',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'target')


# 댓글 추천/비추천
class BaseVoteComment(models.Model):
    """
    상속받는 기본 추천/비추천 모델
    """
    # 투표 하는 유저(from)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 투표 받은 댓글(to)
    target = models.ForeignKey(
        'posts.Comment',
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'target')


class UpVoteComment(BaseVoteComment):
    """
    댓글 추천
    """
    pass


class DownVoteComment(BaseVoteComment):
    """
    댓글 비추천
    """
    pass

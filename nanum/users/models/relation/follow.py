from django.conf import settings
from django.db import models

__all__ = (
    'UserFollow',
    'TopicFollow',
    'TopicExpertiseFollow',
    'TopicInterestFollow',
    'QuestionFollow',
)


class UserFollow(models.Model):
    """
    유저 팔로우
    """
    # 팔로우 하는 유저(from)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following_relations')
    # 팔로우 받는 유저(to)
    target = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='follower_relations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'target')


class TopicFollow(models.Model):
    """
    주제 팔로우
    """
    # 팔로우 하는 유저(from)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # 팔로우 받는 주제(to)
    topic = models.ForeignKey('topics.Topic', on_delete=models.CASCADE)
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # 팔로우 받는 질문(to)
    question = models.ForeignKey('posts.Question', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')

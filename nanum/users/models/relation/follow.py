from django.conf import settings
from django.db import models

__all__ = (
    'UserFollowRelation',
    'TopicFollowRelation',
    'ExpertiseFollowRelation',
    'InterestFollowRelation',
    'QuestionFollowRelation',
)


class UserFollowRelation(models.Model):
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


class TopicFollowRelation(models.Model):
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


class ExpertiseFollowRelation(TopicFollowRelation):
    class Meta:
        unique_together = ('user', 'topic')


class InterestFollowRelation(TopicFollowRelation):
    class Meta:
        unique_together = ('user', 'topic')


class QuestionFollowRelation(models.Model):
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.question.follow_count < 0:
            self.question.follow_count = 1
        else:
            self.question.follow_count += 1
        self.question.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.question.follow_count > 0:
            self.question.follow_count -= 1
        else:
            self.question.follow_count = 0
        self.question.save()

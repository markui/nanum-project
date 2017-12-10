from django.conf import settings
from django.db import models
from django.db.transaction import atomic

from topics.models import Topic
from ...models import CommentPostIntermediate

__all__ = (
    'Question',

)


# user가 None이면 쿼리에서 제외
class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(user=None)


class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=150)
    topics = models.ManyToManyField('topics.Topic', related_name='questions')
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    answer_count = models.IntegerField(null=False, default=0)
    bookmark_count = models.IntegerField(null=False, default=0)
    follow_count = models.IntegerField(null=False, default=0)
    comment_count = models.IntegerField(null=False, default=0)
    objects = QuestionManager()

    def save(self, *args, **kwargs):
        with atomic():
            topics = Topic.objects.select_for_update().filter(pk=self.topics)
            for topic in topics:
                topic.question_count += 1
                topic.save()
            CommentPostIntermediate.objects.get_or_create(question=self)

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with atomic():
            topics = Topic.objects.select_for_update().filter(pk=self.topics)
            for topic in topics:
                topic.question_count -= 1
                topic.save()

            super().delete(*args, **kwargs)

    def __str__(self):
        return f'user: {self.user}, content: {self.content}'

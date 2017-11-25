from django.conf import settings
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

__all__ = (
    'PostType',
    'Comment',
)


class PostType(models.Model):
    """
    PostType 모델
    Comment에 어떤 종류의 포스트와 연결이 되어있는지 설정을 위한 중간 모델
    Reference: https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/
    """
    question = models.OneToOneField(
        'Question',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    answer = models.OneToOneField(
        'Answer',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )


class Comment(MPTTModel):
    """
    Comment 모델
    Modified Preorder Tree Traversal 적용 모델 - Nested Comment 적용
    Generic Foreign Key를 통해 answer/question에 연결될 수 있음
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

    # Nested Comment
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True
    )

    # Question / Answer Foreign Key
    post_type = models.ForeignKey(
        PostType,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.user} - {self.content[:50]}'

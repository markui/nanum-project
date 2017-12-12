from django.conf import settings
from django.db import models
from django.db.models import F
from django.db.transaction import atomic
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

__all__ = (
    'CommentPostIntermediate',
    'Comment',
)


class CommentPostIntermediate(models.Model):
    """
    PostType 모델
    Comment에 어떤 종류의 포스트와 연결이 되어있는지, Question/Answer에 어떤 Comment가 연결되어있는지를 위한 중간모델
    Reference: https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/
    """
    question = models.OneToOneField('Question', null=True, blank=True, on_delete=models.CASCADE,
                                    related_name='comment_post_intermediate')
    answer = models.OneToOneField('Answer', null=True, blank=True, on_delete=models.CASCADE,
                                  related_name='comment_post_intermediate')

    def __str__(self):
        return f'post: {self.post} \ncomment: {self.parent_comments}'

    @property
    def post_type(self):
        if self.question:
            return 'question'
        if self.answer:
            return 'answer'
        raise AssertionError("Neither 'question' or 'answer' set")

    @property
    def post(self):
        """
        해당 post와 연결된 question 혹은 answer와 해당 pk를 반환
        둘 다 없을 경우 raise AssertionError
        :return:
        """
        if self.question:
            return self.question
        if self.answer:
            return self.answer
        raise AssertionError("Neither 'question' or 'answer' set")

    @property
    def parent_comments(self):
        """
        해당 post에 Depth 1에 있는 comment들을 반환
        없을 경우 빈 queryset 반환
        :return:
        """
        return Comment.objects.filter(parent=None, comment_post_intermediate=self.pk)


class Comment(MPTTModel):
    """
    Comment 모델
    Modified Preorder Tree Traversal 적용 모델 - Nested Comment 적용
    Generic Foreign Key를 통해 answer/question에 연결될 수 있음
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # Nested Comment
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children_comments', db_index=True)

    # Question / Answer Foreign Key
    comment_post_intermediate = models.ForeignKey(CommentPostIntermediate, on_delete=models.CASCADE)

    # Upvote, Downvote의 개수
    upvote_count = models.IntegerField(null=False, default=0)
    downvote_count = models.IntegerField(null=False, default=0)

    @property
    def related_post(self):
        """
        Comment 와 엮어 있는 Answer 혹은 Question의 pk를 CommentPostIntermediate 의 to string 방식으로 반환
        :return:
        """
        return self.comment_post_intermediate.post

    @property
    def immediate_children(self):
        """
        Instance 바로 밑에 있는 depth의 Comment object들을 반환
        :return:
        """
        return self.get_children()

    @property
    def immediate_children_count(self):
        """
        Instancen 바로 밑에 있는 depth 의 Comment 개수를 반환
        :return:
        """
        return self.get_children().count()

    @property
    def all_children(self):
        """
        Instance 밑에 있는 모든 Comment object들을 반환
        :return:
        """
        return self.get_descendants(include_self=False)

    @property
    def all_children_count(self):
        """
        Instance 밑에 있는 모든 Comment 개수를 반환
        :return:
        """
        return self.get_descendant_count()

    def __str__(self):
        return f'{self.user} - {self.content[:50]}'

    def save(self, *args, **kwargs):
        """
        Comment가 연결된 Answer 혹은 Question 객체에 대해 comment_count 증가
        :param args:
        :param kwargs:
        :return:
        """
        model = self.comment_post_intermediate.post.__class__

        # race condition 방지
        with atomic():
            post = model.objects.select_for_update().filter(
                comment_post_intermediate=self.comment_post_intermediate
            )
            post.update(comment_count=F('comment_count') + 1)

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Comment 가 연결된 Answer 혹은 Question 객체에 대해 comment_count 감소
        :param args:
        :param kwargs:
        :return:
        """
        model = self.comment_post_intermediate.post.__class__

        # race condition 방지
        with atomic():
            post = model.objects.select_for_update().filter(
                comment_post_intermediate=self.comment_post_intermediate
            )
            post.update(comment_count=F('comment_count') - 1)

            super().delete(*args, **kwargs)

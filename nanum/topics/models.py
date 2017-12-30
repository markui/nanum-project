from io import BytesIO

from django.conf import settings
from django.db import models
from .utils import fields

# Create your models here.


class Topic(models.Model):
    """
    토픽 모델

    """

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    name = models.TextField(max_length=100, unique=True, blank=False, null=False)
    description = models.TextField(max_length=300, blank=True)
    image = fields.DefaultStaticImageField(upload_to='topic', blank=True, null=True,
                                           default_image_path='default_topic_image/topic_image_300.png')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    answer_count = models.IntegerField(null=False, default=0)
    question_count = models.IntegerField(null=False, default=0)
    expert_count = models.IntegerField(null=False, default=0)
    interest_count = models.IntegerField(null=False, default=0)

    def save(self, *args, **kwargs):
        """
        Topic을 제작한 사람은 자동으로 follow
        :param args:
        :param kwargs:
        :return:
        """
        super().save(*args, **kwargs)
        self.expertisefollowrelation_set.get_or_create(user=self.creator, topic=self)
        self.interestfollowrelation_set.get_or_create(user=self.creator, topic=self)

    def recount(self, hard_answer_count=False):
        """
        Topic의 count 필드들의 값을 다시 계산하여 저장
        hard 가 true 일 경우, count 함수를 호출하여 count
        :param field:
        :return:
        """
        questions = self.questions.all()
        answer_count = 0
        if hard_answer_count:
            for question in questions:
                answer_count += question.answer_set.count()
        else:
            for question in questions:
                answer_count += question.answer_count

        question_count = self.questions.count()
        expert_count = self.users_with_expertise.count()
        interest_count = self.users_with_interest.count()

        self.answer_count = answer_count
        self.question_count = question_count
        self.expert_count = expert_count
        self.interest_count = interest_count
        self.save()

    def __str__(self):
        return f'{self.name}, creator:{self.creator}'

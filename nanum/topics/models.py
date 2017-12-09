from django.conf import settings
from django.db import models


# Create your models here.
class Topic(models.Model):
    """
    토픽 모델
    Question과 Answer에 ManyToMany로 연결
    """
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    name = models.TextField(max_length=100, unique=True, blank=False, null=False)
    description = models.TextField(max_length=300, blank=True)
    image = models.ImageField(upload_to='topic', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    answer_count = models.IntegerField(null=False, default=0)
    question_count = models.IntegerField(null=False, default=0)
    expert_count = models.IntegerField(null=False, default=0)
    interest_count = models.IntegerField(null=False, default=0)


    def __str__(self):
        return f'{self.name}, creator:{self.creator}'

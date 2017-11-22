from django.db import models

# Create your models here.
class Topic(models.Model):
    """
    토픽 모델
    Question과 Answer에 Foreinkey로 연결이 되어 있음

    """
    name = models.TextField(
        max_length=200,
    )


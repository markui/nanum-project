from django.db import models



# Create your models here.
class Topic(models.Model):
    """
    토픽 모델
    Question과 Answer에 ManyToMany로 연결
    
    """
    name = models.TextField(
        max_length=200,
    )
    image = models.ImageField(
        upload_to='topic',
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
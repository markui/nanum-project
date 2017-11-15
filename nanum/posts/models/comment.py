from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(

    )
    answer = models.ForeignKey(

    )

from django.db import models
from . import Question

__all__ = (
    'Images',
)


class Images(models.Model):
    question = models.ForeignKey(
        Question,
        blank=True,
        null=True,
    )
    image = models.ImageField(
        upload_to='get_image_filename',
        verbose_name='image',
    )

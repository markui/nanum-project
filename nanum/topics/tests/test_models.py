import datetime

from django.test import TestCase

from ..models import Topic

__all__ = (
    'TopicModelTest',
)


class TopicModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        name = "Computer Science"
        image = ""
        created_at = datetime.datetime.today()
        Topic.objects.create(name=name, image=image, created_at=created_at)

    def test_name_label(self):
        topic = Topic.objects.get(id=1)
        field_label = topic._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')
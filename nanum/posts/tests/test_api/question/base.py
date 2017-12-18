from django.contrib.auth import get_user_model
from rest_framework.test import APILiveServerTestCase

from posts.models import Question
from topics.models import Topic

User = get_user_model()


class QuestionBaseTest(APILiveServerTestCase):
    #
    URL_API_QUESTION_LIST_CREATE_NAME = 'post:question:list'
    URL_API_QUESTION_LIST_CREATE = '/post/question/'

    URL_API_QUESTION_MAIN_FEED_LIST_NAME = 'post:question:main-feed'
    URL_API_QUESTION_MAIN_FEED_LIST = '/post/question/main_feed/'

    @staticmethod
    def create_user(email='siwon@siwon.com', password='dltldnjs'):
        return User.objects.create_user(email=email, password=password)

    @staticmethod
    def create_topic(creator=None, name='temp_topic'):
        return Topic.objects.create(creator=creator, name=name)

    @staticmethod
    def create_question(user=None, content='임시 컨텐츠 입니다.'):
        return Question.objects.create(
            user=user,
            content=content,
        )

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from posts.models import Question
from topics.models import Topic

User = get_user_model()


class QuestionBaseTest(APITestCase):
    # QuestionListCreateView
    URL_API_QUESTION_LIST_CREATE_NAME = 'post:question:list'
    URL_API_QUESTION_LIST_CREATE = '/post/question/'
    # QuestionMainFeedListView
    URL_API_QUESTION_MAIN_FEED_LIST_NAME = 'post:question:main-feed'
    URL_API_QUESTION_MAIN_FEED_LIST = '/post/question/main_feed/'
    # QuestionFilterListView
    URL_API_QUESTION_FILTER_LIST_NAME = 'post:question:topics-filter'
    URL_API_QUESTION_FILTER_LIST = '/post/question/filter/'
    # QuestionRetrieveUpdateDestroyView
    URL_API_QUESTION_RETRIEVE_UPDATE_DESTROY_NAME = 'post:question:detail'
    URL_API_QUESTION_RETRIEVE_UPDATE_DESTROY = '/post/question/{pk}/'

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

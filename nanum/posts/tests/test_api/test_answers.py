from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APILiveServerTestCase, APITestCase

from posts.models import Answer, Question

User = get_user_model()


class AnswerListCreateAPIsTest(APITestCase):
    URL_API_ANSWER_LIST_CREATE_NAME = 'post:answer:user'
    URL_API_ANSWER_MAIN_FEED_LIST_NAME = 'post:answer:main_feed'
    URL_API_ANSWER_BOOKMARK_FEED_LIST_NAME = 'post:answer:bookmark'
    URL_API_ANSWER_FILTER_FEED_LIST_NAME = 'post:answer:filter'

    URL_API_ANSWER_LIST_CREATE = '/post/answer/user/'
    URL_API_ANSWER_MAIN_FEED_LIST = '/post/answer/main_feed/'
    URL_API_ANSWER_BOOKMARK_FEED_LIST = '/post/answer/bookmark/'
    URL_API_ANSWER_FILTER_FEED_LIST = '/post/answer/filter/'

    ANSWER_COUNT_FOR_USER_ONE = 5
    ANSWER_COUNT_FOR_USER_TWO = 10


    @staticmethod
    def create_user(email="abc@abc.com"):
        return User.objects.create_user(email=email, password='password')

    @staticmethod
    def create_answer(user=None, question=None, content=None):
        return Answer.objects.create(user=user, question=question, content=content)

    @staticmethod
    def create_question(user=None):
        return Question.objects.create(user=user, content=f'{user}-질문')

    @classmethod
    def setUpTestData(cls):
        u1 = cls.create_user(email="abc1@abc.com")
        u2 = cls.create_user(email="abc2@abc.com")
        u3 = cls.create_user(email="abc3@abc.com")
        cls.create_question(user=u1)
        question = Question.objects.get(content=f'{u1}-질문')
        # u1으로 답변 2개 생성
        for i in range(cls.ANSWER_COUNT_FOR_USER_ONE):
            cls.create_answer(user=u1, question=question, content=i)
        # u2로 답변 3개 생성
        for j in range(cls.ANSWER_COUNT_FOR_USER_TWO):
            cls.create_answer(user=u2, question=question, content=i)

    # Url Reverse 테스트
    def test_answer_list_url_reverse(self):
        url = reverse(self.URL_API_ANSWER_LIST_CREATE_NAME)
        self.assertEqual(url, self.URL_API_ANSWER_LIST_CREATE)

    def test_answer_main_feed_list_url_reverse(self):
        url = reverse(self.URL_API_ANSWER_MAIN_FEED_LIST_NAME)
        self.assertEqual(url, self.URL_API_ANSWER_MAIN_FEED_LIST)

    def test_answer_bookmark_feed_list_url_reverse(self):
        url = reverse(self.URL_API_ANSWER_BOOKMARK_FEED_LIST_NAME)
        self.assertEqual(url, self.URL_API_ANSWER_BOOKMARK_FEED_LIST)

    def test_answer_filter_feed_list_url_reverse(self):
        url = reverse(self.URL_API_ANSWER_FILTER_FEED_LIST_NAME)
        self.assertEqual(url, self.URL_API_ANSWER_FILTER_FEED_LIST)

    def test_create_answer(self):
        # u1으로 로그인
        self.client.login(email="abc1@abc.com", password="password")

        # 답변 생성
        user = User.objects.get(email="abc1@abc.com").pk
        question = Question.objects.first().pk
        data = {
            'user':user,
            'question':question,
            'content':'새로운 답변입니다',
        }
        response = self.client.post(self.URL_API_ANSWER_LIST_CREATE, data=data)

        # Status 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_answer_list(self):
        """
        유저가 포스트한 답변 list만 나오는지 확인
        :return:
        """
        # u1으로 로그인
        self.client.login(email="abc1@abc.com", password="password")
        response = self.client.get(self.URL_API_ANSWER_LIST_CREATE)

        # Status 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 개수 유저 1이 생성한 개수가 맞는지 확인
        self.assertEqual(len(response.data), self.ANSWER_COUNT_FOR_USER_ONE)

    def test_get_answer_list_when_not_authenticated(self):
        """
        유저가 로그인 되지 않았을 시 403에러를 올리는지 확인
        :return:
        """
        response = self.client.get(self.URL_API_ANSWER_LIST_CREATE)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_answer_main_feed_list_view(self):
        pass

    def test_answer_bookmark_feed_list_view(self):
        pass

    def test_answer_filter_feed_list_view(self):
        pass

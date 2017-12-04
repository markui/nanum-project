from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from rest_framework import status

from posts.models import Answer, Question
from .custom_base import AnswerBaseTest
from topics.models import Topic

User = get_user_model()


class AnswerListCreateAPIsTest(AnswerBaseTest):
    # Url Reverse 테스트
    def test_answer_list_url_reverse(self):
        url = reverse(self.URL_API_ANSWER_LIST_CREATE_NAME)
        self.assertEqual(url, self.URL_API_ANSWER_LIST_CREATE)

    def test_answer_main_feed_list_url_reverse(self):
        url = reverse(self.URL_API_ANSWER_MAIN_FEED_LIST_NAME)
        self.assertEqual(url, self.URL_API_ANSWER_MAIN_FEED_LIST)

    def test_create_answer(self):
        u1_email = self.USER_EMAIL_LIST[0]
        u1 = User.objects.get(email=u1_email)
        self.client.force_authenticate(user=u1)

        # 답변 생성
        question = Question.objects.first().pk

        data = {
            'user': u1.pk,
            'question': question,
            'content': self.ANSWER_CONTENT,
        }
        response = self.client.post(self.URL_API_ANSWER_LIST_CREATE, data=data, format='json')
        # Status 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_answer_list(self):
        """
        유저가 포스트한 답변 list만 나오는지 확인
        :return:
        """
        u1_email = self.USER_EMAIL_LIST[0]
        u1 = User.objects.get(email=u1_email)
        self.client.force_authenticate(user=u1)

        url = self.URL_API_ANSWER_LIST_CREATE + '?' + self.URL_FILTER_USER.format(pk=u1.pk)
        response = self.client.get(url)

        answer = Answer.objects.filter(user=u1)
        # Status 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 개수 유저 1이 생성한 개수가 맞는지 확인
        self.assertEqual(response.data['count'], answer.count())

    def test_get_answer_list_when_not_authenticated(self):
        """
        유저가 로그인 되지 않았을 시 401에러를 올리는지 확인
        :return:
        """
        response = self.client.get(self.URL_API_ANSWER_LIST_CREATE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_answer_main_feed_list_view(self):
        pass

    def test_answer_bookmark_feed_list_view(self):
        pass

    def test_answer_filter_feed_list_view(self):
        pass

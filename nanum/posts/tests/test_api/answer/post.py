from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from rest_framework import status
from posts.models import Answer, Question
from ...custom_base import CustomBaseTest

User = get_user_model()


class AnswerCreateTest(CustomBaseTest):
    """
    url :       /post/answer/
    method :    Create

    Answer Post에 대한 테스트

    """

    def test_create_answer(self):
        """
        Content, Content_html, question과  user가 data에 들어갔을 때 답변이 잘 생성되는지 확인
        :return:
        """
        u1_email = self.USER_EMAIL_LIST[0]
        u1 = User.objects.get(email=u1_email)
        self.client.force_authenticate(user=u1)
        question = Question.objects.first().pk

        # 답변 생성
        data = {
            'user': u1.pk,
            'question': question,
            'content': self.ANSWER_DELTA,
            'content_html': self.ANSWER_HTML,
        }
        response = self.client.post(self.URL_API_ANSWER_LIST_CREATE, data=data, format='json')
        # Status 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 생성된 Answer Object의 content가 집어넣은 Answer Delta와 일치하는지 확인
        answer = Answer.objects.get(pk=response.data['pk'])
        self.assertEqual(answer.content, self.ANSWER_DELTA)

        # 생성된 Answer Object의 content_html이 집어넣은 Answer HTML과 일치하는지 확인
        answer_soup = BeautifulSoup(answer.content_html, 'html.parser')
        original_soup = BeautifulSoup(self.ANSWER_HTML, 'html.parser')
        self.assertEqual(str(answer_soup), str(original_soup))

    def test_create_answer_without_content_unable_to_publish(self):
        """
        Content가 없는 답변에 published가 True인 data가 왔을 때 Error가 반환되는지 확인
        :return:
        """

        u1_email = self.USER_EMAIL_LIST[0]
        u1 = User.objects.get(email=u1_email)
        self.client.force_authenticate(user=u1)

        # 답변 생성
        question = Question.objects.first().pk

        data = {
            'user': u1.pk,
            'question': question,
            'published': True,
        }
        response = self.client.post(self.URL_API_ANSWER_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_answer_without_content_or_content_html(self):
        """
        Content가 왔을 때 content html이 안오거나 content_html이 왔을 때 content가 오면 Error가 반환되는지 확인
        :return:
        """
        u1_email = self.USER_EMAIL_LIST[0]
        u1 = User.objects.get(email=u1_email)
        self.client.force_authenticate(user=u1)

        # 답변 생성
        question = Question.objects.first().pk

        data = {
            'user': u1.pk,
            'question': question,
            'content': self.ANSWER_DELTA,
        }
        response = self.client.post(self.URL_API_ANSWER_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'user': u1.pk,
            'question': question,
            'content_html': self.ANSWER_HTML
        }
        response = self.client.post(self.URL_API_ANSWER_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

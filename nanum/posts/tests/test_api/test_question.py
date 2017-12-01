import string
from random import randrange

from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APILiveServerTestCase

from posts.apis import QuestionListCreateView
from posts.models import Question

User = get_user_model()

class QuestionListCreateViewTest(APILiveServerTestCase):
    URL_API_QUESTION_CREATE_NAME = 'posts:question:question-create'
    URL_API_QUESTION_CREATE = '/posts/question/'
    VIEW_CLASS = QuestionListCreateView

    # 원하는 URL과 실제로 만들어지는 URL 같은지 검사
    def test_question_create_url_name_reverse(self):
        url = reverse(self.URL_API_QUESTION_CREATE_NAME)
        print(f'reverse test : {url}')
        self.assertEqual(url, self.URL_API_QUESTION_CREATE)

    # 같은 view의 class인지 검사
    def test_question_create_url_resolve_view_class(self):
        resolve_match = resolve(self.URL_API_QUESTION_CREATE)
        print(f'view class test : {resolve_match.func.view_class}')
        self.assertEqual(resolve_match.func.view_class,
                         self.VIEW_CLASS.as_view().view_class)

    # 임의의 유저로 question objects 생성
    def test_get_question_list(self):
        user = User.objects.create_user(email='siwon@siwon.com')
        num = randrange(20)
        for i in range(num):
            question = Question.objects.create(
                user=user,
                topics='topic',
                content='content',
            )
            print(f'topic : {question.topics}, content : {question.content}')
        url = reverse(self.URL_API_QUESTION_CREATE_NAME)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((Question.objects.count(), num))
        self.assertEqual(len(response.data), num)

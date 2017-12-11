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
    URL_API_QUESTION_CREATE_NAME = 'post:question:question-list'
    URL_API_QUESTION_CREATE = '/post/question/'
    VIEW_CLASS = QuestionListCreateView

    # URL name으로 원하는 URL과 실제로 만들어지는 URL 같은지 검사
    def test_question_create_url_name_reverse(self):
        url = reverse(self.URL_API_QUESTION_CREATE_NAME)
        print(f'reverse test : {url}')
        self.assertEqual(url, self.URL_API_QUESTION_CREATE)

    # URL이 실제 URL name을 참조하고 있는지 검사
    def test_question_create_url_name_resolve(self):
        resolve_match = resolve(self.URL_API_QUESTION_CREATE)
        print(f'resolve test(url name) : {resolve_match.namespace + ":" + resolve_match.url_name}')
        self.assertEqual(resolve_match.namespace + ":" + resolve_match.url_name, self.URL_API_QUESTION_CREATE_NAME)

    # 같은 view의 class인지 검사
    # .func 는 임시함수, .as_view() 또한 함수이다. 참조하는 주소 값이 다르므로 .func.view_class 로 비교
    # self.VIEW_CLASS == self.VIEW_CLASS.as_view().view_class : True
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

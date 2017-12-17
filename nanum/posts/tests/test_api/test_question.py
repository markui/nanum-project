from pprint import pprint
from random import randrange

from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APILiveServerTestCase

from posts.apis import QuestionListCreateView
from posts.models import Question
from topics.models import Topic

User = get_user_model()


class QuestionListCreateViewTest(APILiveServerTestCase):
    URL_API_QUESTION_CREATE_NAME = 'post:question:list'
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

    # 임의의 유저로 question objects 생성 및 확인
    def test_get_post_question_list(self):
        user = User.objects.create_user(email='siwon@siwon.com')
        topic1 = Topic.objects.create(creator=user, name='토픽1')
        topic2 = Topic.objects.create(creator=user, name='토픽2')
        topic3 = Topic.objects.create(creator=user, name='토픽3')
        num = randrange(20)
        for index, i in enumerate(range(num)):
            question = Question.objects.create(
                user=user,
                content=f'{index+1}번째 content',
            )
            question.topics.add(topic1)
            question.topics.add(topic2)
            question.topics.add(topic3)
            print(f'{index+1}번째\n content : {question.content}\n')

        url = reverse(self.URL_API_QUESTION_CREATE_NAME)
        print(f'url : {url}')
        response = self.client.get(url)
        # status code가 200인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 객체의 수가 num과 같은지 확인
        # json리스트의 길이로 비교하게 되면 count, previous, next, result 무조건 4가 출력된다.
        counted_objects = response.data.get('count')
        print(f'response.data.get(\'count\') : {counted_objects}')
        self.assertEqual(counted_objects, num)

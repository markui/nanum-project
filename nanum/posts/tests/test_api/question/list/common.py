import random
from random import randint
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from rest_framework import status

from posts.apis import (
    QuestionListCreateView,
)
from ..base import QuestionBaseTest

User = get_user_model()


class QuestionListCreateCommonViewTest(QuestionBaseTest):
    VIEW_CLASS = QuestionListCreateView

    # URL name으로 원하는 URL과 실제로 만들어지는 URL 같은지 검사
    def test_question_create_url_name_reverse(self):
        url = reverse(self.URL_API_QUESTION_LIST_CREATE_NAME)
        print(f'reverse test : {url}')
        self.assertEqual(url, self.URL_API_QUESTION_LIST_CREATE)

    # URL이 실제 URL name을 참조하고 있는지 검사
    def test_question_create_url_name_resolve(self):
        resolve_match = resolve(self.URL_API_QUESTION_LIST_CREATE)
        print(f'resolve test(url name) : {resolve_match.namespace + ":" + resolve_match.url_name}')
        self.assertEqual(resolve_match.namespace + ":" + resolve_match.url_name, self.URL_API_QUESTION_LIST_CREATE_NAME)

    # 같은 view의 class인지 검사
    # .func 는 임시함수, .as_view() 또한 함수이다. 참조하는 주소 값이 다르므로 .func.view_class 로 비교
    # self.VIEW_CLASS == self.VIEW_CLASS.as_view().view_class : True
    def test_question_create_url_resolve_view_class(self):
        resolve_match = resolve(self.URL_API_QUESTION_LIST_CREATE)
        print(f'view class test : {resolve_match.func.view_class}')
        self.assertEqual(resolve_match.func.view_class,
                         self.VIEW_CLASS.as_view().view_class)

    # user가 None이면 제외되는지 확인
    # # user단에서 none객체 생성을 막아놓아서 테스트 불가
    def test_get_question_list_exclude_user_is_none(self):
        """
        user가 None인 Question이 QuestionList get 요청에서 제외되는지 테스트
        :return:
        """
        user = self.create_user()
        # user = self.create_user(is_none=True)

        num_user_none_questions = randint(1, 10)
        num_questions = randint(11, 20)
        # default user는 None
        for i in range(num_user_none_questions):
            self.create_question()
        for i in range(num_questions):
            self.create_question(user=user)

        response = self.client.get(self.URL_API_QUESTION_LIST_CREATE)
        counted_question = response.data.get('count')
        # user가 없는 Question객체는 response에 포함되지 않는지 확인
        self.assertEqual(counted_question, num_questions)

    # query parameters 필터링 확인
    def test_get_question_list_filter_is_working(self):
        """
        query_params로의 필터링이 잘 작동하는지 확인

        ?page=1 : count 0~4
        ?page=2 : count 5~9
        ?page=3 : count 10~14
        :return:
        """
        temp_user = self.create_user()
        # print(f'temp_user : {temp_user.pk}')
        self.create_question(user=temp_user)
        temp_topic = self.create_topic(creator=temp_user)
        url = reverse(self.URL_API_QUESTION_LIST_CREATE_NAME)
        response = self.client.get(url)
        num_of_questions = response.data.get('count')
        max_page = int((num_of_questions / 5)) + 1

        print('====하나의 쿼리 파라미터를 포함한 URL====')
        # 하나의 query parameter에 대해 검사
        for query_param in self.query_params:
            if query_param == 'topic':
                url += f'?{query_param}={temp_topic.pk}'
            elif query_param == 'page':
                url += f'?{query_param}={max_page}'
            else:
                url += f'?{query_param}={temp_user.pk}'
            response = self.client.get(url)
            # status code가 200인지 확인
            print(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            url = reverse(self.URL_API_QUESTION_LIST_CREATE_NAME)

        print('\n하나의 query parameter에 대한 테스트 성공!\n')

        print('====연속적인 쿼리 파라미터를 포함한 URL====')
        # cascade한 query parameters에 대해서 검사
        num_of_query_params = randint(1, len(self.query_params))
        # query_params 중 임의의 값을 1부터 len(query_params) 사이의 임의의 값 만큼 순회하여 확인
        for i in range(num_of_query_params):
            random_query_of_query_params = random.choice(self.query_params)
            print(random_query_of_query_params)
            if random_query_of_query_params == 'topic':
                url += f'?{random_query_of_query_params}={temp_topic.pk}'
            elif random_query_of_query_params == 'page':
                url += f'?{random_query_of_query_params}={max_page}'
            else:
                url += f'?{random_query_of_query_params}={temp_user.pk}'
            print(f'url : {url}')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        print('\ncascade한 query parameters에 대한 테스트 성공!\n')

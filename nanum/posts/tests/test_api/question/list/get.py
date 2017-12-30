import json

from django.core import serializers
from django.http import JsonResponse
from django.urls import reverse
from rest_framework import status

from posts.apis import QuestionFilterListView
from posts.models import Question
from posts.serializers import QuestionGetSerializer
from ..base import QuestionBaseTest


class QuestionListViewTest(QuestionBaseTest):
    """
    url :       /post/question/
    method :    GET

    1. QuestionList의 Get요청에 대한 테스트(test_get_question_list)
       - Get 요청으로 질문들에 대한 리스트를 임의의 값으로 테스트 하기 위해
         유저, 토픽, 질문 생성에 대한 테스트를 내부적으로 진행하였다.

    2. QuestionList의 Pagination에 대한 테스트(test_question_pagination_list)
       - 임의의 page를 테스트하기 위해서 위 테스트와 마찬가지로
         유저, 토픽, 질문 생성에 대한 테스트를 내부적으로 진행하였다.
    """
    VIEW_CLASS = QuestionFilterListView

    def test_get_question_base(self):

        # 유저 생성(queryset 리턴)
        users_queryset = self.create_random_users()
        # 토픽 생성
        topics_queryset = self.create_random_topics(users_queryset)
        # 질문 생성
        question_queryset = self.create_random_questions(users_queryset, topics_queryset)

        return question_queryset

    def test_get_pagination_question(self):
        """
        QuestionList의 Get요청에 대한 테스트
        임의의 개수만큼 Question을 생성하고 해당 개수만큼 Response가 돌아오는지 확인
        완전히 렌더링 된 response의 검사보단 response의 생성된 데이터를 테스트

        Question List에 대한 Pagination 테스트
        pagination 테스트를 하려면 Question이 생성되어 있어야 하므로
        Question 객체들을 생성 후 리스트를 가져오는 테스트를 선행한다.
        """
        print("\n\n**********QuestionList의 Get요청에 대한 테스트입니다.*********\n")
        print("\n\n**********QuestionList의 Pagination에 대한 테스트입니다.*********\n")

        # Question list를 가져오는 테스트 선행
        question_queryset = self.test_get_question_base()

        # /post/question/
        url = reverse(self.URL_API_QUESTION_LIST_CREATE_NAME)
        # page
        page = 1
        url += f'?page={page}'
        response = self.client.get(url)
        # status code가 200인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # response로 돌아온 객체들이 각각 count, next, previous, results키를 가지고 있는지 확인
        cur_data = response.data
        self.assertIn('count', cur_data)
        self.assertIn('next', cur_data)
        self.assertIn('previous', cur_data)
        self.assertIn('results', cur_data)

        print('====테스트 할 URL====')
        result_index = 0
        print('http://testserver' + f'{url}')
        # page별로 request url을 다르게 주어 response.data 각각 확인
        for i in range(self.num_of_questions):
            if result_index == 5:
                url = response.data.get('next')
                response = self.client.get(url)
                print(url)
                cur_data = response.data
                result_index = 0

            # results가 question, topics키를 가지고 있는지 확인
            cur_results_data = cur_data.get('results')[result_index]
            self.assertIn('question', cur_results_data)
            self.assertIn('topics', cur_results_data)
            # question이 아래의 키들을 가지고 있는지 확인
            cur_question_data = cur_results_data.get('question')
            # pk = cur_question_data.get('pk')
            # print(f'pk : {pk}')
            self.assertIn('pk', cur_question_data)
            self.assertIn('url', cur_question_data)
            self.assertIn('user', cur_question_data)
            self.assertIn('content', cur_question_data)
            self.assertIn('bookmark_count', cur_question_data)
            self.assertIn('follow_count', cur_question_data)
            self.assertIn('comment_count', cur_question_data)
            self.assertIn('created_at', cur_question_data)
            self.assertIn('modified_at', cur_question_data)

            # ===========results.get('question') 테스트===========

            # 테스트 arguments
            cur_question_pk = cur_question_data.get('pk')
            cur_question_content = cur_question_data.get('content')
            cur_question_url = cur_question_data.get('url')
            cur_question_user = cur_question_data.get('user')

            # question.pk 테스트
            question_queryset_pk = question_queryset.get(pk=cur_question_pk).pk
            self.assertEqual(cur_question_pk, question_queryset_pk)

            # question.content 테스트
            question_queryset_content = question_queryset.get(pk=cur_question_pk).content
            self.assertEqual(cur_question_content, question_queryset_content)

            # question.url 테스트
            question_queryset_url = f'http://testserver/post/question/{cur_question_pk}/'
            self.assertEqual(cur_question_url, question_queryset_url)

            # question.user 테스트
            question_queryset_user = f'http://testserver/user/{cur_question_pk}/profile/main-detail/'
            self.assertEqual(cur_question_user, question_queryset_user)

            # ===========results.get('topics') 테스트===========
            topics_list = list()

            # 테스트 arguments
            cur_topics_data = cur_results_data.get('topics')

            # topics 테스트
            question = question_queryset.get(pk=cur_question_pk)
            topics = question.topics.all()

            for topic in topics:
                topics_list.append(f'http://testserver/topic/{topic.pk}/')

            self.assertEqual(topics_list, cur_topics_data)

            # ?page='현재페이지' 의 if index == 5, page skip
            print(f'현재 페이지의 index : {result_index}')
            result_index += 1

        print('\ntest_question_pagination_list 테스트 성공!\n')

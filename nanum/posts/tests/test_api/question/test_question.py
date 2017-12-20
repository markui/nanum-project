from random import randint
import random

from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from rest_framework import status

from posts.apis import (
    QuestionListCreateView,
    QuestionMainFeedListView,
    QuestionRetrieveUpdateDestroyView,
    QuestionFilterListView,
)
from posts.models import Question
from posts.tests.test_api.question.base import QuestionBaseTest

User = get_user_model()


class QuestionCreateViewTest(QuestionBaseTest):
    """
    Question Objects 생성 테스트입니다.
    Question의 파라미터로 Topic 객체가 들어가므로 여러 Topic을 생성 후
    Question 객체의 생성을 테스트 합니다.
    url :       /post/question/
    method :    post
    """

    def test_create_question(self):
        # 토픽 리스트를 저장 할 리스트
        topic_list = list()
        # /post/question/
        url = self.URL_API_QUESTION_LIST_CREATE
        # print(url)
        user = self.create_user()
        self.client.force_authenticate(user=user)
        topics = self.create_random_topics(user=user)
        # 토픽의 pk를 하나씩 리스트에 저장
        for topic in topics:
            topic_list.append(topic.pk)
        # print(f'topics : {topic_list}')
        data = {
            'content': 'create question test content',
            'topics': topic_list,
        }
        print(f'data : {data}')

        response = self.client.post(url, data=data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class QuestionListViewTest(QuestionBaseTest):
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
        """
        posts.apis.question.QuestionListCreateView 뷰에 대해
        URL reverse, resolve, 사용하고 있는 view함수가 같은지 확인
        """
        resolve_match = resolve(self.URL_API_QUESTION_LIST_CREATE)
        print(f'view class test : {resolve_match.func.view_class}')
        self.assertEqual(resolve_match.func.view_class,
                         self.VIEW_CLASS.as_view().view_class)

    # 임의의 유저로 question objects 생성 및 확인
    def test_get_question_list(self):
        """
        QuestionList의 Get요청 (Post목록)에 대한 테스트
        임의의 개수만큼 Question을 생성하고 해당 개수만큼 Response가 돌아오는지 확인
        :return:
        """
        # 유저 생성
        self.create_random_users()
        print(f'====User.objects.all()====\n : {User.objects.all()}')
        # 질문 생성
        self.create_random_questions()
        print(f'====Queestion.objects.all()====\n : {Question.objects.all()}')

        url = reverse(self.URL_API_QUESTION_LIST_CREATE_NAME)
        # page
        page = 1
        url += f'?page={page}'
        print(f'url : {url}')
        response = self.client.get(url)
        # status code가 200인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # response로 돌아온 객체들이 각각 count, next, previous, results키를 가지고 있는지 확인
        cur_data = response.data
        self.assertIn('count', cur_data)
        self.assertIn('next', cur_data)
        self.assertIn('previous', cur_data)
        self.assertIn('results', cur_data)

        # page별로 request url을 다르게 주어 response.data 각각 확인
        result_index = 0
        for index, i in enumerate(range(self.num_of_questions)):
            if result_index == 5:
                url = response.data.get('next')
                response = self.client.get(url)
                print(url)
                cur_data = response.data
                result_index = 0
            print(f'index : {index}')

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

            print(f'result_index : {result_index}')
            result_index += 1

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
            print(f'url of query_param : {url}')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            print(f'response : {response}')
            url = reverse(self.URL_API_QUESTION_LIST_CREATE_NAME)

        # 연속적인 query parameters에 대해서 검사
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


class QuestionMainFeedListViewTest(QuestionBaseTest):
    VIEW_CLASS = QuestionMainFeedListView

    # URL name으로 원하는 URL과 실제로 만들어지는 URL 같은지 검사
    def test_question_main_feed_create_url_name_reverse(self):
        url = reverse(self.URL_API_QUESTION_MAIN_FEED_LIST_NAME)
        print(f'reverse test : {url}')
        self.assertEqual(url, self.URL_API_QUESTION_MAIN_FEED_LIST)

    # URL이 실제 URL name을 참조하고 있는지 검사
    def test_question_main_feed_create_url_name_resolve(self):
        resolve_match = resolve(self.URL_API_QUESTION_MAIN_FEED_LIST)
        print(f'resolve test(url name) : '
              f'{resolve_match.namespace + ":" + resolve_match.url_name}')
        self.assertEqual(resolve_match.namespace + ":" + resolve_match.url_name,
                         self.URL_API_QUESTION_MAIN_FEED_LIST_NAME)

    # 같은 view의 class인지 검사
    # .func 는 임시함수, .as_view() 또한 함수이다. 참조하는 주소 값이 다르므로 .func.view_class 로 비교
    # self.VIEW_CLASS == self.VIEW_CLASS.as_view().view_class : True
    def test_question_main_feed_create_url_resolve_view_class(self):
        """
        posts.apis.question. QuestionMainFeedListView뷰에 대해
        URL reverse, resolve, 사용하고 있는 view함수가 같은지 확인
        :return:
        """
        resolve_match = resolve(self.URL_API_QUESTION_MAIN_FEED_LIST)
        print(f'view class test : {resolve_match.func.view_class}')
        self.assertEqual(resolve_match.func.view_class,
                         self.VIEW_CLASS.as_view().view_class)

    # main-feed
    def test_get_question_main_feed_list(self):
        pass


class QuestionRetrieveUpdateDestroyViewTest(QuestionBaseTest):
    VIEW_CLASS = QuestionRetrieveUpdateDestroyView

    def test_question_create_and_retrieve_object(self):
        temp_user = self.create_user()
        temp_question = self.create_question(user=temp_user)
        print(f'temp_question : {temp_question.pk}')

        response = self.client.get(f'http://testserver/post/question/{temp_question.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class QuestionFilterListViewTest(QuestionBaseTest):
    VIEW_CLASS = QuestionFilterListView

    # URL name으로 원하는 URL과 실제로 만들어지는 URL 같은지 검사
    def test_question_filter_create_url_name_reverse(self):
        url = reverse(self.URL_API_QUESTION_FILTER_LIST_NAME)
        print(f'reverse test : {url}')
        self.assertEqual(url, self.URL_API_QUESTION_FILTER_LIST)

    # URL이 실제 URL name을 참조하고 있는지 검사
    def test_question_filter_create_url_name_resolve(self):
        resolve_match = resolve(self.URL_API_QUESTION_FILTER_LIST)
        print(f'resolve test(url name) : '
              f'{resolve_match.namespace + ":" + resolve_match.url_name}')
        self.assertEqual(resolve_match.namespace + ":" + resolve_match.url_name,
                         self.URL_API_QUESTION_FILTER_LIST_NAME)

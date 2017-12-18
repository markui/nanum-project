from random import randrange, randint

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
from topics.models import Topic

User = get_user_model()


class QuestionListCreateViewTest(QuestionBaseTest):
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
        :return:
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
        # user = User.objects.create_user(
        #     email='siwon@siwon.com',
        #     password='dltldnjs'
        # )
        user = self.create_user()
        topic1 = self.create_topic(creator=user, name='토픽1')
        topic2 = self.create_topic(creator=user, name='토픽2')
        topic3 = self.create_topic(creator=user, name='토픽3')
        num = randrange(10, 30)
        for index, i in enumerate(range(num)):
            question = self.create_question(
                user=user,
                content=f'{index+1}번째 컨텐츠 입니다.',
            )
            question.topics.add(topic1)
            question.topics.add(topic2)
            question.topics.add(topic3)
            print(f'question.content : {question.content}')

        url = reverse(self.URL_API_QUESTION_LIST_CREATE_NAME)
        # page
        page = 1
        url += f'?page={page}'
        print(f'url : {url}')
        response = self.client.get(url)
        # status code가 200인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # objects.count 결과가 num과 같은지 확인
        self.assertEqual(Question.objects.count(), num)
        # 객체의 수가 num과 같은지 확인
        # json리스트의 길이로 비교하게 되면 count, previous, next, results 무조건 4 출력
        counted_objects = response.data.get('count')
        print(f'response.data.get(\'count\') : {counted_objects}')
        self.assertEqual(counted_objects, num)

        # response로 돌아온 객체들이 각각 count, next, previous, results키를 가지고 있는지 확인
        cur_data = response.data
        self.assertIn('count', cur_data)
        self.assertIn('next', cur_data)
        self.assertIn('previous', cur_data)
        self.assertIn('results', cur_data)

        # page별로 request url을 다르게 주어 response.data 각각 확인
        result_index = 0
        for index, i in enumerate(range(num)):
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

    def test_get_question_list_exclude_user_is_none(self):
        """
        user가 None인 Question가 QuestionList get 요청에서 제외되는지 테스트
        :return:
        """
        user = self.create_user()
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


class QuestionMainFeedListViewTest(QuestionBaseTest):
    VIEW_CLASS = QuestionMainFeedListView

    # URL name으로 원하는 URL과 실제로 만들어지는 URL 같은지 검사
    def test_question_create_url_name_reverse(self):
        url = reverse(self.URL_API_QUESTION_MAIN_FEED_LIST_NAME)
        print(f'reverse test : {url}')
        self.assertEqual(url, self.URL_API_QUESTION_MAIN_FEED_LIST)

    # URL이 실제 URL name을 참조하고 있는지 검사
    def test_question_create_url_name_resolve(self):
        resolve_match = resolve(self.URL_API_QUESTION_MAIN_FEED_LIST)
        print(f'resolve test(url name) : {resolve_match.namespace + ":" + resolve_match.url_name}')
        self.assertEqual(resolve_match.namespace + ":" + resolve_match.url_name,
                         self.URL_API_QUESTION_MAIN_FEED_LIST_NAME)

    # 같은 view의 class인지 검사
    # .func 는 임시함수, .as_view() 또한 함수이다. 참조하는 주소 값이 다르므로 .func.view_class 로 비교
    # self.VIEW_CLASS == self.VIEW_CLASS.as_view().view_class : True
    def test_question_create_url_resolve_view_class(self):
        """
        posts.apis.question. QuestionMainFeedListView뷰에 대해
        URL reverse, resolve, 사용하고 있는 view함수가 같은지 확인
        :return:
        """
        resolve_match = resolve(self.URL_API_QUESTION_MAIN_FEED_LIST)
        print(f'view class test : {resolve_match.func.view_class}')
        self.assertEqual(resolve_match.func.view_class,
                         self.VIEW_CLASS.as_view().view_class)


class QuestionRetrieveUpdateDestroyViewTest(QuestionBaseTest):
    pass


class QuestionFilterListViewTest(QuestionBaseTest):
    pass

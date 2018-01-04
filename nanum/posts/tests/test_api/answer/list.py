from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from posts.models import Answer
from posts.serializers import AnswerGetSerializer, AnswerPostSerializer
from ...custom_base import CustomBaseTest

User = get_user_model()


class AnswerListTest(CustomBaseTest):
    """
    url :       /post/answer/
    method :    GET

    Answer List에 대한 테스트

    """

    # Url Reverse 테스트
    def test_answer_list_url_reverse(self):
        url = reverse(self.URL_API_ANSWER_LIST_CREATE_NAME)
        self.assertEqual(url, self.URL_API_ANSWER_LIST_CREATE)

    def test_get_answer_list_when_not_authenticated(self):
        """
        유저가 로그인 되지 않았을 시 401에러를 올리는지 확인
        :return:
        """
        response = self.client.get(self.URL_API_ANSWER_LIST_CREATE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_serializer_change_on_request_type(self):
        """
        Request 종류에 따라 serializer가 바뀌는지 확인
        :return:
        """
        get_response = self.client.get(self.URL_API_ANSWER_LIST_CREATE)
        get_serializer = get_response.renderer_context['view'].get_serializer()

        post_response = self.client.post(self.URL_API_ANSWER_LIST_CREATE)
        post_serializer = post_response.renderer_context['view'].get_serializer()

        self.assertIsInstance(get_serializer, AnswerGetSerializer)
        self.assertIsInstance(post_serializer, AnswerPostSerializer)

    def test_get_list_view_with_wrong_query_params(self):
        """
        URI에 입력 불가능한 query parameter가 갔을 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?not_possible=1')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_list_view_without_query_param_value(self):
        """
        URI에 query parameter가 들어갔는데 값이 안들어 갔을 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?topic=')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_list_view_with_query_params_not_matching_type(self):
        """
        Query Parameter에 적합한 type이 아닌 값이 들어갔을 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?topic=a')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_list_view_single_query_paramter(self):
        """
        가능한 Query parameter에 대해 200 response가 반환되는지 확인 (Page, ordering 제외)
        POSSIBLE QUERY PARAMETERS : topic, user, bookmarked_by

        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        query_paramters = ['topic', 'user', 'bookmarked_by']
        for query in query_paramters:
            response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?{query}=1')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_view_query_topic(self):
        """
        Query Parameter에 Topic으로 필터한 답변의 개수가 실제로 quesiton__topics에 대해 필터한 답변의 개수와 일치하는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user.token)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?topic=1')
        self.assertEqual(response.data.get('count'), Answer.objects.filter(question__topics=1).count())

    def test_get_list_view_query_user(self):
        """
        Query Parameter에 user으로 필터한 답변의 개수가 실제로 user에 대해 필터한 답변의 개수와 일치하는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user.token)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?user=1')
        self.assertEqual(response.data.get('count'), Answer.objects.filter(user=1).count())

    def test_get_list_view_query_bookmarked_by(self):
        """
        Query Parameter에 bookmarked_by로 필터한 답변의 개수가
        Answer중 bookmarked user에 user가 포함되는 Answer와 일치하는지 확인
        현재 Bookmark 기능 미개발로 잠정 comment out
        :return:
        """
        # user = User.objects.first()
        # answer = Answer.objects.first()
        # AnswerBookmarkRelation.objects.create(user=user, answer=answer)
        #
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + user.token)
        # url= f'{self.URL_API_ANSWER_LIST_CREATE}?bookmarked_by={user.pk}'
        # response = self.client.get(url)
        # self.assertEqual(response.data.get('count'), Answer.objects.filter(answerbookmarkrelation__user=user.pk).count())
        pass

    def test_get_list_with_ordering_query_paramter(self):
        """
        List View가 ordering parameter에 대해 값을 돌려주는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?ordering=created_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?ordering=modified_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_view_with_list_of_values(self):
        """
        Query Parameter에 여러개의 값을 넣어서 필터가 가능한지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?user=1,2')
        answers_by_users = Answer.objects.filter(user=1) | Answer.objects.filter(user=2)
        self.assertEqual(response.data.get('count'), answers_by_users.count())

    def test_get_list_pagination_default_pagesize(self):
        """
        List Pagination을 통해 뽑는 page size가 5인지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.URL_API_ANSWER_LIST_CREATE)
        self.assertEqual(len(response.data['results']), 5)

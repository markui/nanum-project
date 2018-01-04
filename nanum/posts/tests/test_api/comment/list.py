from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from posts.serializers import CommentCreateSerializer, CommentSerializer
from ...custom_base import CustomBaseTest

User = get_user_model()


class CommentListTest(CustomBaseTest):
    """
    url :       /post/comment/
    method :    GET

    Comment List에 대한 테스트
    """

    def test_comment_list_url_reverse(self):
        """
        URL 이 잘 Reverse가 되는지 테스트
        :return:
        """
        url = reverse(self.URL_API_COMMENT_LIST_CREATE_NAME)
        self.assertEqual(url, self.URL_API_COMMENT_LIST_CREATE)

    def test_get_comment_list_when_not_authenticated(self):
        """
        유저가 로그인 되지 않았을 시 200이 오는 지 확인
        :return:
        """
        response = self.client.get(self.URL_API_COMMENT_LIST_CREATE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_serializer_change_on_request_type(self):
        """
        Request 종류에 따라 serializer가 바뀌는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        get_response = self.client.get(self.URL_API_COMMENT_LIST_CREATE)
        get_serializer = get_response.renderer_context['view'].get_serializer()

        post_response = self.client.post(self.URL_API_COMMENT_LIST_CREATE)
        post_serializer = post_response.renderer_context['view'].get_serializer()

        self.assertIsInstance(get_serializer, CommentSerializer)
        self.assertIsInstance(post_serializer, CommentCreateSerializer)

    def test_get_list_view_with_wrong_query_params(self):
        """
        URI에 입력 불가능한 query parameter가 갔을 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_COMMENT_LIST_CREATE}?not_possible=1')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_list_view_without_query_param_value(self):
        """
        URI에 query parameter가 들어갔는데 값이 안들어 갔을 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_COMMENT_LIST_CREATE}?topic=')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_list_view_with_query_params_not_matching_type(self):
        """
        Query Parameter에 적합한 type이 아닌 값이 들어갔을 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_COMMENT_LIST_CREATE}?topic=a')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_list_view_single_query_paramter(self):
        """
        가능한 Query parameter에 대해 200 response가 반환되는지 확인 (Page, ordering 제외)
        POSSIBLE QUERY PARAMETERS : topic, user, bookmarked_by

        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        query_paramters = ['user', 'question', 'answer']
        for query in query_paramters:
            response = self.client.get(f'{self.URL_API_COMMENT_LIST_CREATE}?{query}=1')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

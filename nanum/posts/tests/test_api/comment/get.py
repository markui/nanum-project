from django.contrib.auth import get_user_model
from rest_framework import status

from posts.models import Comment, Answer
from posts.tests.custom_base import CustomBaseTest

User = get_user_model()


class CommentGetTest(CustomBaseTest):
    """
    url :       /post/comment/<pk>
    method :    GET

    Comment Get에 대한 테스트
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        parent = Comment.objects.first()
        user = User.objects.first()
        question = parent.related_post

        comments = []
        # 첫번째 코멘트 밑(depth 1)에 코멘트 10개 생성
        for i in range(10):
            c = cls.create_comment(user=user, question=question, parent=parent)
            comments.append(c)

        # depth1의 코멘트에 대해 코멘트 5개씩 생성
        # 즉, 총 50개 코멘트 추가 생성
        # 원래 parent 코멘트 밑에는 depth1에 10게 + depth2에 50개의 children이 생김
        for comment in comments:
            for i in range(5):
                c = cls.create_comment(user=user, question=question, parent=comment)

    def test_comment_retrieve(self):
        """
        유저가 로그인 되어 있을 시 200이 오는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.URL_API_COMMENT_DETAIL.format(pk=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_retrieve_when_not_authenticated(self):
        """
        유저가 로그인 되지 않았을 시 400이 오는 지 확인
        :return:
        """
        response = self.client.get(self.URL_API_COMMENT_DETAIL.format(pk=1))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_retrieve_with_wrong_query_param(self):
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_COMMENT_DETAIL.format(pk=1)}?not_possible=1')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_retrieve_without_query_param_value(self):
        """
        URI에 query parameter가 들어갔는데 값이 안들어 갔을 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_COMMENT_DETAIL.format(pk=1)}?all_children=')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_retrieve_with_query_params_not_matching_type(self):
        """
        Query Parameter에 적합한 type이 아닌 값이 들어갔을 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_COMMENT_DETAIL.format(pk=1)}?topic=a')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_retrieve_single_query_paramter(self):
        """
        가능한 Query parameter에 대해 200 response가 반환되는지 확인 (Page, ordering 제외)
        POSSIBLE QUERY PARAMETERS : topic, user, immedate_children, all_children

        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        query_paramters = ['all_children', 'immediate_children']
        for query in query_paramters:
            response = self.client.get(f'{self.URL_API_COMMENT_DETAIL.format(pk=1)}?{query}=True')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_retrieve_pagination_for_all_children(self):
        """
        Comment Retrieve의 all_children에 대한 pagination이 실행되는지 테스트

        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_COMMENT_DETAIL.format(pk=1)}?all_children=True')
        self.assertEqual(response.data["all_children_count"], 60)
        self.assertEqual("all_children" in response.data, True)

    def test_comment_retrieve_pagination_for_immediate_children(self):
        """
        Comment Retrieve의 immediate_children에 대한 pagination이 실행되는지 테스트

        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_COMMENT_DETAIL.format(pk=1)}?immediate_children=True')
        self.assertEqual(response.data["immediate_children_count"], 10)
        self.assertEqual("immediate_children" in response.data, True)
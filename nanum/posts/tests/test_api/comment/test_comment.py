from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from posts.models import Question, Answer, Comment
from posts.serializers import CommentCreateSerializer, CommentSerializer
from ...custom_base import CustomBaseTest

User = get_user_model()

class CommentListTest(CustomBaseTest):
    def test_comment_list_url_reverse(self):
        """

        :return:
        """
        url = reverse(self.URL_API_COMMENT_LIST_CREATE_NAME)
        self.assertEqual(url, self.URL_API_COMMENT_LIST_CREATE)

    def test_get_answer_list_when_not_authenticated(self):
        """
        유저가 로그인 되지 않았을 시 401에러를 올리는지 확인
        :return:
        """
        response = self.client.get(self.URL_API_COMMENT_LIST_CREATE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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


class CommentPostTest(CustomBaseTest):
    def test_comment_on_question_post(self):
        """

        :return:
        """
        user = User.objects.first()
        question = Question.objects.first()
        content = "질문입니다."
        data = {
            'user': user.pk,
            'question': question.pk,
            'content': content,
        }

        self.client.force_authenticate(user=user)
        response = self.client.post(self.URL_API_COMMENT_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_on_answer_post(self):
        """

        :return:
        """
        user = User.objects.first()
        answer = Answer.objects.first()
        content = "질문입니다."
        data = {
            'user': user.pk,
            'answer': answer.pk,
            'content': content,
        }

        self.client.force_authenticate(user=user)
        response = self.client.post(self.URL_API_COMMENT_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_on_comment_post(self):
        """

        :return:
        """
        parent = Comment.objects.first()
        user = User.objects.first()
        answer = Answer.objects.first()
        content = "질문입니다."
        data = {
            'user': user.pk,
            'answer':answer.pk,
            'parent': parent.pk,
            'content': content,
        }

        self.client.force_authenticate(user=user)
        response = self.client.post(self.URL_API_COMMENT_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_without_answer_or_question(self):
        """
        Answer과 Question이 없이 Comment를 생성하려 할 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        content = "질문입니다."
        data = {
            'user': user.pk,
            'content': content,
        }

        self.client.force_authenticate(user=user)
        response = self.client.post(self.URL_API_COMMENT_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_with_invalid_question(self):
        """

        :return:
        """
        user = User.objects.first()
        content = "질문입니다."
        data = {
            'user': user.pk,
            'question': 1000000,
            'content': content,
        }

        self.client.force_authenticate(user=user)
        response = self.client.post(self.URL_API_COMMENT_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_with_invalid_ansewr(self):
        """

        :return:
        """
        user = User.objects.first()
        content = "질문입니다."
        data = {
            'user': user.pk,
            'answer': 10000000,
            'content': content,
        }

        self.client.force_authenticate(user=user)
        response = self.client.post(self.URL_API_COMMENT_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from django.contrib.auth import get_user_model
from rest_framework import status

from posts.models import Question, Answer, Comment
from ...custom_base import CustomBaseTest

User = get_user_model()


class CommentPostTest(CustomBaseTest):
    """
    url :       /post/comment/
    method :    POST

    Comment Post에 대한 테스트
    """

    def test_comment_on_question_post(self):
        """
        Question 대하여 comment를 post 할 때 테스트
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
        Answer 에 대하여 comment를 post 할 때 테스트
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
        Comment 에 대하여 comment를 post 할 때 테스트
        :return:
        """
        parent = Comment.objects.first()
        user = User.objects.first()
        answer = Answer.objects.first()
        content = "질문입니다."
        data = {
            'user': user.pk,
            'answer': answer.pk,
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
        존재하지 않는 Question에 대해 Comment를 생성하려 할 때 에러가 나는지 확인
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
        존재하지 않는 Answer에 대해 Comment를 생성하려 할 때 에러가 나는지 확인
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

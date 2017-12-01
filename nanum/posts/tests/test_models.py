from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import *

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        u1 = User.objects.create_user(
            name="김 경훈",
            email="abc1@abc.com",
            facebook_user_id=12345677,
            password="12345678",
        )
        u2 = User.objects.create_user(
            name="서상원",
            email="abc2@abc.com",
            password="12345678",
        )
        q1 = Question.objects.create(
            user=u1,
            content="질문 내용",
        )
        a1 = Answer.objects.create(
            user=u2,
            question=q1,
            content="답변1 내용"
        )
        qc1 = Comment.objects.create(
            user=u2,
            content="질문1 코멘트 내용",
            post_manager=PostManager.objects.get(question=q1),
        )
        qc1_nested_1 = Comment.objects.create(
            user=u1,
            content="질문1 코멘트 nested 코멘트",
            post_manager=PostManager.objects.get(question=q1),
            parent=qc1,
        )
        ac1 = Comment.objects.create(
            user=u1,
            content="질문1 답변1 코멘트 내용",
            post_manager=PostManager.objects.get(answer=a1),
        )
        ac1_nested_1 = Comment.objects.create(
            user=u2,
            content="질문1 답변1 nested 코멘트",
            post_manager=PostManager.objects.get(answer=a1),
            parent=ac1,
        )
        ac1_nested_1 = Comment.objects.create(
            user=u2,
            content="질문1 답변1 nested 코멘트",
            post_manager=PostManager.objects.get(answer=a1),
            parent=ac1,
        )

    def test_nested_comment_root_equal_root(self):
        qc1 = Comment.objects.get(pk=1)
        qc1_nested_1 = Comment.objects.get(pk=2)
        self.assertEqual(qc1_nested_1.get_root(), qc1)

    def test_comment_string_method(self):
        """
        Comment 모델 __str__ 함수 테스트
        :return:
        """
        ac1_nested_1 = Comment.objects.get(pk=4)
        self.assertEqual(str(ac1_nested_1), "abc2@abc.com - 질문1 답변1 nested 코멘트")

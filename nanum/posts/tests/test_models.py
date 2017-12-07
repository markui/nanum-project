from django.contrib.auth import get_user_model

from posts.tests.test_api.custom_base import AnswerBaseTest
from ..models import *

User = get_user_model()


class CommentModelTest(AnswerBaseTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        u1 = User.objects.get(pk=1)
        u2 = User.objects.get(pk=2)
        q1 = Question.objects.get(pk=1)
        a1 = Answer.objects.get(pk=1)

        qc1 = Comment.objects.create(
            user=u2,
            content="질문1 코멘트 내용",
            comment_post_intermediate=CommentPostIntermediate.objects.get(question=q1),
        )
        qc1_nested_1 = Comment.objects.create(
            user=u1,
            content="질문1 코멘트 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(question=q1),
            parent=qc1,
        )
        ac1 = Comment.objects.create(
            user=u1,
            content="질문1 답변1 코멘트 내용",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=a1),
        )
        ac1_nested_1 = Comment.objects.create(
            user=u2,
            content="질문1 답변1 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=a1),
            parent=ac1,
        )
        ac1_nested_1 = Comment.objects.create(
            user=u2,
            content="질문1 답변1 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=a1),
            parent=ac1,
        )

    def test_comment_string_method(self):
        """
        Comment 모델 __str__ 함수 테스트
        :return:
        """
        ac1_nested_1 = Comment.objects.get(pk=4)
        self.assertEqual(str(ac1_nested_1), "abc2@abc.com - 질문1 답변1 nested 코멘트")

    def test_comment_related_post_property(self):
        """
        Comment 모델 related_post property 테스트
        :return:
        """
        pass

    def test_upvote_count_field(self):
        """
        Comment 모델 upvote_count 필드 테스트
        :return:
        """
        pass

    def test_downvote_count_field(self):
        """
        Comment 모델 downvote_count 필드 테스트
        :return:
        """
        pass
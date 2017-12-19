from django.contrib.auth import get_user_model

from posts.tests.test_api.custom_base import AnswerBaseTest
from ..models import *

User = get_user_model()


class CommentModelTest(AnswerBaseTest):
    @classmethod
    def setUpTestData(cls):
        user = cls.create_user(name="abc@abc.com", email="abc@abc.com")
        topic = cls.create_topic(user=user, name="토픽")
        question = cls.create_question(user=user, topic=topic)
        answer = cls.create_answer(user=user, question=question)

        qc1 = Comment.objects.create(
            user=user,
            content="질문 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(question=question),
        )
        Comment.objects.create(
            user=user,
            content="질문 코멘트 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(question=question),
            parent=qc1,
        )
        ac1 = Comment.objects.create(
            user=user,
            content="답변 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=answer),
        )
        ac1_nested_1 = Comment.objects.create(
            user=user,
            content="답변 nested 코멘트 1",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=answer),
            parent=ac1,
        )
        Comment.objects.create(
            user=user,
            content="답변 nested 코멘트 1 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=answer),
            parent=ac1_nested_1,
        )
        Comment.objects.create(
            user=user,
            content="답변 nested 코멘트 2 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=answer),
            parent=ac1_nested_1,
        )


    def test_comment_string_method(self):
        """
        Comment 모델 __str__ 함수 테스트
        :return:
        """
        ac1_nested_1 = Comment.objects.get(pk=4)
        self.assertEqual(str(ac1_nested_1), "abc@abc.com - 답변 nested 코멘트 1")

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
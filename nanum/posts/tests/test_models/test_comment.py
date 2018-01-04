from django.contrib.auth import get_user_model

from posts.models import *
from topics.models import Topic
from ..custom_base import CustomBaseTest

User = get_user_model()


class CommentPostIntermediateModelTest(CustomBaseTest):
    """
    Model : CommentPostIntermediate

    """
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
        ac1_immediate = Comment.objects.create(
            user=user,
            content="답변 nested 코멘트 1",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=answer),
            parent=ac1,
        )
        Comment.objects.create(
            user=user,
            content="답변 nested 코멘트 1 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=answer),
            parent=ac1_immediate,
        )
        Comment.objects.create(
            user=user,
            content="답변 nested 코멘트 2 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=answer),
            parent=ac1_immediate,
        )

    def test_created_when_post_created(self):
        """
        Question이나 Answer가 생성될 때 CommentPostIntermediate이 생성되는지 확인
        :return:
        """
        user = User.objects.get(name="abc@abc.com")
        topic = Topic.objects.get(name="토픽")
        question = self.create_question(user=user, topic=topic)
        answer = self.create_answer(user=user, question=question)
        cpi_question = CommentPostIntermediate.objects.get(question=question)
        cpi_answer = CommentPostIntermediate.objects.get(answer=answer)

        self.assertEqual(cpi_question.question, question)
        self.assertEqual(cpi_answer.answer, answer)

    def test_post_type_property(self):
        """
        CommentPostIntermediate 모델 post_type property 테스트
        :return:
        """
        question = Question.objects.first()
        answer = Answer.objects.first()

        cpi_question = CommentPostIntermediate.objects.get(question=question)
        cpi_answer = CommentPostIntermediate.objects.get(answer=answer)

        self.assertEqual(cpi_question.post_type, 'question')
        self.assertEqual(cpi_answer.post_type, 'answer')

    def test_post_property(self):
        """
        CommentPostIntermediate 모델 post property 테스트
        :return:
        """
        question = Question.objects.first()
        answer = Answer.objects.first()

        cpi_question = CommentPostIntermediate.objects.get(question=question)
        cpi_answer = CommentPostIntermediate.objects.get(answer=answer)

        self.assertIsInstance(cpi_question.post, Question)
        self.assertIsInstance(cpi_answer.post, Answer)

    def test_parent_comments_property(self):
        """
        CommentPostIntermediate 모델 parent_comment property 테스트
        :return:
        """
        question = Question.objects.first()
        answer = Answer.objects.first()

        cpi_question = CommentPostIntermediate.objects.get(question=question)
        cpi_answer = CommentPostIntermediate.objects.get(answer=answer)

        self.assertEqual(cpi_question.parent_comments.count(),
                         Comment.objects.filter(comment_post_intermediate=cpi_question, parent=None).count()
                         )
        self.assertEqual(cpi_answer.parent_comments.count(),
                         Comment.objects.filter(comment_post_intermediate=cpi_answer, parent=None).count()
                         )


class CommentModelTest(CustomBaseTest):
    """
    Model : Comment

    """
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
        ac1_immediate = Comment.objects.create(
            user=user,
            content="답변 nested 코멘트 1",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=answer),
            parent=ac1,
        )
        Comment.objects.create(
            user=user,
            content="답변 nested 코멘트 1 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=answer),
            parent=ac1_immediate,
        )
        Comment.objects.create(
            user=user,
            content="답변 nested 코멘트 2 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=answer),
            parent=ac1_immediate,
        )

    def test_comment_string_method(self):
        """
        Comment 모델 __str__ 함수 테스트
        :return:
        """

        ac1_immediate = Comment.objects.first()
        self.assertEqual(str(ac1_immediate), "abc@abc.com - 질문 코멘트")

    def test_comment_related_post_property(self):
        """
        Comment 모델 related_post property 테스트
        :return:
        """
        qc1 = Comment.objects.first()
        q = qc1.comment_post_intermediate.question
        # qc1.related_post 가 Question Instance인지 확인하고,
        # 해당 값이 comment_post_intermediate.question으로 들어간 값과 일치하는지 확인
        self.assertIsInstance(qc1.related_post, Question)
        self.assertEqual(qc1.related_post, q)

    def test_comment_immediate_children_property(self):
        """
        Comment 모델 immediate_children property 테스트
        :return:
        """
        qc1 = Comment.objects.get(content="질문 코멘트")
        qc1_immediate_child = Comment.objects.get(content="질문 코멘트 nested 코멘트")
        ac1 = Comment.objects.get(content="답변 코멘트")
        ac1_immediate_child = Comment.objects.get(content="답변 nested 코멘트 1")
        ac1_immediate_child_child = Comment.objects.get(content="답변 nested 코멘트 1 nested 코멘트")
        # qc1.immediate_children에 qc1_immediate이 있는지 확인
        self.assertIn(qc1_immediate_child, qc1.immediate_children)

        # ac1.immediate_children에 ac1_immediate_child 있는지 확인하고,
        # ac1_immediate_child 의 자식인 ac1_immediate_child_child 이 없는지 확인
        self.assertIn(ac1_immediate_child, ac1.immediate_children)
        self.assertNotIn(ac1_immediate_child_child, ac1.immediate_children)

    def test_comment_immediate_children_count_property(self):
        """
        Comment 모델 immediate_children_count property 테스트
        :return:
        """
        qc1 = Comment.objects.get(content="질문 코멘트")
        ac1 = Comment.objects.get(content="답변 코멘트")
        self.assertEqual(qc1.immediate_children_count, qc1.immediate_children.count())
        self.assertEqual(ac1.immediate_children_count, ac1.immediate_children.count())

    def test_comment_all_children_property(self):
        """
        Comment 모델 all_children property 테스트
        :return:
        """
        ac1 = Comment.objects.get(content="답변 코멘트")
        ac1_immediate_child = Comment.objects.get(content="답변 nested 코멘트 1")
        ac1_immediate_child_child = Comment.objects.get(content="답변 nested 코멘트 1 nested 코멘트")
        ac1_immediate_child_child2 = Comment.objects.get(content="답변 nested 코멘트 2 nested 코멘트")

        # Depth 2에 있는 ac1_immediate_child_child 와 ac1_immediate_child_child2 가
        # ac1.all_children에 포함되어 있는지 확인
        self.assertIn(ac1_immediate_child_child, ac1.all_children)
        self.assertIn(ac1_immediate_child_child2, ac1.all_children)

    def test_comment_all_children_count_property(self):
        """
        Comment 모델 all_children_count property 테스트
        :return:
        """
        ac1 = Comment.objects.get(content="답변 코멘트")
        self.assertEqual(ac1.all_children_count, ac1.all_children.count())

    def test_related_post_comment_count_increment(self):
        """
        Comment 모델과 연결된 post의 comment_count가
        Comment가 생성되거나 삭제될 때 increment가 되는지 테스트
        :return:
        """
        user = User.objects.get(name="abc@abc.com", email="abc@abc.com")
        topic = Topic.objects.get(creator=user, name="토픽")
        q = Question.objects.get(user=user)
        a = Answer.objects.get(user=user, question=q)

        q_comment_count_before = q.comment_count
        a_comment_count_before = a.comment_count

        Comment.objects.create(
            user=user,
            content="질문 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(question=q),
        )
        Comment.objects.create(
            user=user,
            content="질문 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=a),
        )

        q = Question.objects.get(user=user)
        a = Answer.objects.get(user=user, question=q)
        q_comment_count_after = q.comment_count
        a_comment_count_after = a.comment_count

        self.assertEqual(q_comment_count_after - q_comment_count_before, 1)
        self.assertEqual(a_comment_count_after - a_comment_count_before, 1)

    def test_related_post_comment_count_decrement(self):
        """
        Comment 모델과 연결된 post의 comment_count가
        Comment가 삭제될 때 decrement가 되는지 테스트 - 가장 마지막 Depth
        :return:
        """
        user = User.objects.get(name="abc@abc.com", email="abc@abc.com")
        topic = Topic.objects.get(creator=user, name="토픽")
        q = Question.objects.get(user=user)
        a = Answer.objects.get(user=user, question=q)

        q_comment_count_before = q.comment_count
        a_comment_count_before = a.comment_count

        cq = Comment.objects.get(
            user=user,
            content="질문 코멘트 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(question=q),
        )
        ca = Comment.objects.get(
            user=user,
            content="답변 nested 코멘트 2 nested 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=a),
        )
        cq.delete()
        ca.delete()

        q = Question.objects.get(user=user)
        a = Answer.objects.get(user=user, question=q)
        q_comment_count_after = q.comment_count
        a_comment_count_after = a.comment_count

        self.assertEqual(q_comment_count_before - q_comment_count_after, 1)
        self.assertEqual(a_comment_count_before - a_comment_count_after, 1)

    def test_children_comment_cascade_delete(self):
        """
        Comment 모델과 연결된 post의 comment_count가
        Children이 있는 Comment가 삭제되었을 때 해당 Children의 개수 + 1 만큼 decrement 되는지 테스트
        :return:
        """
        user = User.objects.get(name="abc@abc.com", email="abc@abc.com")
        topic = Topic.objects.get(creator=user, name="토픽")
        q = Question.objects.get(user=user)
        a = Answer.objects.get(user=user, question=q)

        q_comment_count_before = q.comment_count
        a_comment_count_before = a.comment_count

        q_parent_comment = Comment.objects.get(
            user=user,
            content="질문 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(question=q),
        )
        a_parent_comment = Comment.objects.get(
            user=user,
            content="답변 코멘트",
            comment_post_intermediate=CommentPostIntermediate.objects.get(answer=a),
        )

        q_children_count = q_parent_comment.all_children_count + 1
        a_children_count = a_parent_comment.all_children_count + 1

        q_parent_comment.delete()
        a_parent_comment.delete()

        q = Question.objects.get(user=user)
        a = Answer.objects.get(user=user, question=q)
        q_comment_count_after = q.comment_count
        a_comment_count_after = a.comment_count

        self.assertEqual(q_comment_count_before - q_comment_count_after, q_children_count)
        self.assertEqual(a_comment_count_before - a_comment_count_after, a_children_count)

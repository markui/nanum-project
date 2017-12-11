from rest_framework import serializers
from rest_framework.exceptions import ParseError

from ..models import Comment, CommentPostIntermediate, Answer, Question

__all__ = (
    'CommentCreateSerializer',
    'CommentSerializer',
)


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    METHOD: CREATE
    user, parent, question, answer, content를 데이터로 받음
    CommentPostIntermediate을 통해 question / answer과 연결되며, related_post로 해당 정보를 보여줌
    """
    question = serializers.IntegerField(required=False)
    answer = serializers.IntegerField(required=False)
    user = serializers.HyperlinkedIdentityField(
        view_name='user:profile-detail',
        lookup_field='user_id',
        lookup_url_kwarg='pk',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = (
            'pk',
            'user',
            'related_post',
            'parent',
            'content',
            'question',
            'answer',
            'created_at',
            'modified_at',
        )
        read_only_fields = (
            'pk',
            'related_post',
            'created_at',
            'modified_at',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        post_type = self.initial_data.get('question') or self.initial_data.get('answer')
        parent = self.initial_data.get('parent', None)

        if post_type == 'question':
            view_name = 'post:question:question-detail'
        else:
            view_name = 'post:answer:answer-detail'

        self.fields['related_post'] = serializers.HyperlinkedIdentityField(
            view_name=view_name,
            lookup_field='related_post',
            lookup_url_kwarg='pk',
            read_only=True,
        )

        if parent:
            self.fields['parent'] = serializers.HyperlinkedIdentityField(
                view_name='post:comment:comment-detail',
                lookup_field='parent_id',
                lookup_url_kwarg='pk',
                read_only=True,
            )

    def validate_answer(self, value):
        try:
            Answer.objects.get(pk=value)
        except:
            raise ParseError({"error": "해당 pk의 답변이 존재하지 않습니다."})
        return value

    def validate_question(self, value):
        try:
            Question.objects.get(pk=value)
        except:
            raise ParseError({"error": "해당 pk의 질문이 존재하지 않습니다."})
        return value

    def validate(self, data):
        """
        Answer 혹은 Question값이 필수적으로 들어왔는지 Validate
        - Refactor 가능한지?
        :param data:
        :return:
        """
        if not data.get('answer', None) and not data.get('question', None):
            raise ParseError(detail="Question, Answer 중 한개의 값은 있어야 합니다.")
        return data

    @property
    def request_user(self):
        """
        Request를 보낸 유저를 반환
        :return:
        """
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

    def save(self, **kwargs):
        """
        serializers.py 의 save method override
        validated_data에서 question 과 answer를 통해 comment 연결된 CommentPostIntermediate object를 get,
        해당 값을 넣어 Comment를 저장

        :param kwargs:
        :return:
        """
        question = self.validated_data.pop("question", None)
        answer = self.validated_data.pop("answer", None)
        if question:
            comment_post_intermediate = CommentPostIntermediate.objects.get(question=question)
        elif answer:
            comment_post_intermediate = CommentPostIntermediate.objects.get(answer=answer)
        else:
            raise ParseError(detail={"error": "Question, Answer 중 한개의 값은 있어야 합니다."})

        super().save(
            user=self.request_user,
            comment_post_intermediate=comment_post_intermediate,
            **kwargs
        )



class CommentSerializer(serializers.ModelSerializer):
    """
    METHOD: GET
    모든 값이 read_only
    all_children_count, 즉 밑에 달린 댓글의 총 개수 또한 반환
    """
    user = serializers.HyperlinkedIdentityField(
        view_name='user:profile-detail',
        lookup_field='user_id',
        lookup_url_kwarg='pk',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = (
            'pk',
            'user',
            'related_post',
            'parent',
            'created_at',
            'modified_at',
            'upvote_count',
            'downvote_count',
            'all_children_count',
        )
        read_only_fields = (
            'pk',
            'user',
            'related_post',
            'parent',
            'created_at',
            'modified_at',
            'upvote_count',
            'downvote_count',
            'all_children_count',
            'content',
        )

    def __init__(self, *args, **kwargs):
        """
        Override serializer __init__
        Serializer가 initialize가 되기전에 동적으로 related_post를 설정

        :param args:
        :param kwargs:
        """
        comment = args[0]
        if comment.comment_post_intermediate.post_type == 'question':
            view_name = 'post:question:question-detail'
        else:
            view_name = 'post:answer:answer-detail'

        self.fields['related_post'] = serializers.HyperlinkedIdentityField(
            view_name=view_name,
            lookup_field='related_post',
            lookup_url_kwarg='pk',
            read_only=True,
        )

        if comment.parent:
            self.fields['parent'] = serializers.HyperlinkedIdentityField(
                view_name='post:comment:comment-detail',
                lookup_field='parent_id',
                lookup_url_kwarg='pk',
                read_only=True,
            )

        super().__init__(*args, **kwargs)

from rest_framework import serializers
from rest_framework.exceptions import ParseError

from ..models import Comment, CommentPostIntermediate

__all__ = (
    'CommentCreateSerializer',
    'CommentGetSerializer',
    'CommentUpdateSerializer',
)


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    METHOD: CREATE
    user, parent, question, answer, content를 데이터로 받음
    CommentPostIntermediate을 통해 question / answer과 연결되며, related_post로 해당 정보를 보여줌
    """
    question = serializers.IntegerField(required=False)
    answer = serializers.IntegerField(required=False)

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
            raise ParseError(detail={"error":"Question, Answer 중 한개의 값은 있어야 합니다."})

        super().save(
            user=self.request_user,
            comment_post_intermediate=comment_post_intermediate,
            **kwargs
        )


class CommentGetSerializer(serializers.ModelSerializer):
    """
    METHOD: GET
    모든 값이 read_only
    all_children_count, 즉 밑에 달린 댓글의 총 개수 또한 반환
    """

    class Meta:
        model = Comment
        fields = (
            'pk',
            'user',
            'related_post',
            'parent',
            'content',
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
            'all_children_count',
            'content',
        )


class CommentUpdateSerializer(serializers.ModelSerializer):
    """
    METHOD: PUT, PATCH
    content 만 form에서 받을 수 있도록 설정
    """

    class Meta:
        model = Comment
        fields = (
            'pk',
            'user',
            'related_post',
            'parent',
            'content',
            'created_at',
            'modified_at',
        )
        read_only_fields = (
            'pk',
            'user',
            'related_post',
            'parent',
            'created_at',
            'modified_at',
        )

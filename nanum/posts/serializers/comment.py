from rest_framework import serializers

from ..models import Comment, CommentPostIntermediate

__all__ = (
    'CommentSerializer',
    'CommentUpdateSerializer',
)


class CommentSerializer(serializers.ModelSerializer):
    question = serializers.IntegerField(required=False)
    answer = serializers.IntegerField(required=False)

    class Meta:
        model = Comment
        fields = (
            'user',
            'content',
            'question',
            'answer',
            'parent',

            'pk',
            'related_post',
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
            raise serializers.ValidationError("Question, Answer 중 한개의 값은 있어야 합니다.")
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
            raise serializers.ValidationError({"save_error": ["Question, Answer 중 한개의 값은 있어야 합니다."]})

        super().save(
            user=self.request_user,
            comment_post_intermediate=comment_post_intermediate,
            **kwargs
        )


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'content',

            'pk',
            'user',
            'related_post',
            'parent',
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

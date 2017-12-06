from rest_framework import serializers

from ..models import Comment, CommentPostIntermediate

__all__ = (
    'CommentSerializer',
)


class CommentSerializer(serializers.ModelSerializer):
    question = serializers.IntegerField(required=False)
    answer = serializers.IntegerField(required=False)

    class Meta:
        model = Comment
        fields = (
            'pk',
            'user',
            'content',
            'related_post',
            'question',
            'answer',
            'parent',
            'created_at',
            'modified_at',
        )

    def validate(self, data):
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

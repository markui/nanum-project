from rest_framework import serializers

from ..models import QuestionComment, AnswerComment, NestedComment

__all__ = (
    'QuestionCommentSerializer',
    'AnswerCommentSerializer',
    'NestedCommentSerializer',
)


class QuestionCommentSerializer(serializers.Modelserializer):
    class Meta:
        model = QuestionComment
        fields = (
            'question',
            'user',
            'comment',
            'created_at',
            'modified_at',
        )


class AnswerCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerComment
        fields = (
            'answer',
            'user',
            'comment',
            'created_at',
            'modified_at',
        )


class NestedCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NestedComment
        fields = (
            'parent_comment',
            'user',
            'comment',
            'created_at',
            'modified_at',
        )

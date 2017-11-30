from rest_framework import serializers

from ..models import Answer

__all__ = (
    'AnswerSerializer',
)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            'pk',
            'user',
            'question',
            'content',
        )
        read_only_fields = (
            'created_at',
            'modified_at',
        )


class AnswerFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        read_only_fields = (
            'pk',
            'user',
            'content',
            'created_at',
            'modified_at',
        )
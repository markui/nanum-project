from rest_framework import serializers

from ..models import Question

__all__ = (
    'QuestionSerializer',
)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'pk',
            'user',
            'topic',
            'content',
            'created_at',
        )

        read_only_fields = (
            'user',
            'created_at',
        )
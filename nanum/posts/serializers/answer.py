from rest_framework import serializers

from ..models import Answer

__all__ = (
    'AnswerSerializer',
    'AnswerUpdateSerializer',
    'AnswerFeedSerializer',
)


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = (
            'pk',
            'user',
            'question',
            'content',
            'published',
            'created_at',
            'modified_at',
        )

    def validate_content(self):
        
        pass

class AnswerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            'question',
            'content',
            'published',
        )
        read_only_fields = (
            'pk',
            'user',
            'created_at',
            'modified_at',
        )

class AnswerFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        read_only_fields = (
            'pk',
            'user',
            'questoin',
            'content',
            'created_at',
            'modified_at',
        )

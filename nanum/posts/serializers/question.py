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
            'topics',
            'content',
            'created_at',
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        topics = ret['topics']
        del ret['topics']
        data = {
            'question': ret,
            'topics': topics,
        }
        return data



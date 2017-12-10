from django.template.defaultfilters import length
from rest_framework import serializers
from ..models import Question

__all__ = (
    'QuestionGetSerializer',
    'QuestionPostSerializer',
    'QuestionUpdateDestroySerializer',
)


class QuestionGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'pk',
            'user',
            'topics',
            'content',
            'created_at',
            'modified_at',
        )
        read_only_fields = (
            'pk',
            'user',
            'created_at',
            'modified_at',
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


class QuestionPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'pk',
            'user',
            'topics',
            'content',
            'created_at',
            'modified_at',
        )
        read_only_fields = (
            'pk',
            'user',
            'created_at',
            'modified_at',
        )

    def validate(self, data):
        if length(data['content']) < 10:
            raise serializers.ValidationError("질문이 너무 짧습니다. 10자 이상 작성해주세요.")
        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        topics = ret['topics']
        del ret['topics']
        data = {
            'question': ret,
            'topics': topics,
        }
        return data


class QuestionUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'pk',
            'user',
            'topics',
            'content',
            'created_at',
            'modified_at',
        )
        read_only_fields = (
            'pk',
            'user',
            'created_at',
            'modified_at',
        )

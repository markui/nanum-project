from django.template.defaultfilters import length
from rest_framework import serializers

from topics.models import Topic
from ..models import Question

__all__ = (
    'QuestionGetSerializer',
    'QuestionPostSerializer',
    'QuestionUpdateSerializer',

)

# Deserialize
topics = serializers.ListField(
    # 리스트 내의 object의 유효성 검증에 사용하는 필드 인스턴스
    child=serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(),
        write_only=True,
    )
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
        )
        read_only_fields = (
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


class QuestionPostSerializer(serializers.ModelSerializer):
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

    def validate(self, validated_data):
        if length(validated_data['content']) < 10:
            raise serializers.ValidationError("질문이 너무 짧습니다. 10자 이상 작성해주세요.")
        return validated_data




class QuestionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'pk',
            'user',
            'topics',
            'content',
            'created_at',
        )

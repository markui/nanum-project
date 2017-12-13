from django.template.defaultfilters import length
from rest_framework import serializers

from ..models import Question

__all__ = (
    'QuestionGetSerializer',
    'QuestionPostSerializer',
    'QuestionUpdateDestroySerializer',
)


class QuestionGetSerializer(serializers.ModelSerializer):
    # 해당 질문의 detail 페이지
    url = serializers.HyperlinkedIdentityField(
        lookup_field='pk',
        read_only=True,
        view_name='post:question:question-detail',
    )
    # 해당 유저의 프로필 페이지
    user = serializers.HyperlinkedRelatedField(
        lookup_field='pk',
        read_only=True,
        view_name='user:profile-main-detail',
    )
    # 해당 질문이 속하는 토픽들의 detail 페이지
    topics = serializers.HyperlinkedRelatedField(
        lookup_field='pk',
        many=True,
        read_only=True,
        view_name='topic:topic-detail',
    )

    class Meta:
        model = Question
        fields = (
            'pk',
            'url',
            'user',
            'topics',
            'content',
            'bookmark_count',
            'follow_count',
            'comment_count',
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
            'url',
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

    def validate(self, data):
        if length(data['content']) < 10:
            raise serializers.ValidationError("질문이 너무 짧습니다. 10자 이상 작성해주세요.")
        return data

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import IntegerField
from rest_framework.relations import PrimaryKeyRelatedField

from topics.models import Topic
from users.models import InterestFollowRelation, ExpertiseFollowRelation, UserFollowRelation, QuestionFollowRelation

User = get_user_model()

__all__ = (
    'TopicFollowRelationSerializer',
)


class TopicFollowRelationSerializer(serializers.Serializer):
    """
    주제(관심분야/전문분야) 팔로우를 위한 Serializer
    """
    pk = IntegerField(label='ID', read_only=True)
    user = PrimaryKeyRelatedField(read_only=True)
    topic = PrimaryKeyRelatedField(queryset=Topic.objects.all(), required=True)

    def validate_topic(self, value):
        """
        이미 팔로우하고 있는 주제인지 확인
        """
        TopicModel = InterestFollowRelation if self.context['type'] == 'interest' else ExpertiseFollowRelation

        if TopicModel.objects.filter(user=self.context['request'].user, topic=value).exists():
            raise serializers.ValidationError('이미 팔로우하고 있는 주제입니다.')
        return value

    def create(self, validated_data):
        """
        전문분야/관심분야 모두 TopicFollowRelationSerializer를 공통으로
        사용하게 하기 위해서, APIView에서 어떤 분야인지를 판별해주는,
        self.context['type']을 받아옴
        """
        if self.context['type'] == 'interest':
            return InterestFollowRelation.objects.create(
                user=validated_data['user'],
                topic=validated_data['topic']
            )

        elif self.context['type'] == 'expertise':
            return ExpertiseFollowRelation.objects.create(
                user=validated_data['user'],
                topic=validated_data['topic']
            )


class UserFollowRelationSerializer(serializers.ModelSerializer):
    """
    유저 팔로우를 위한 Serializer
    """

    class Meta:
        model = UserFollowRelation
        fields = (
            'pk',
            'user',
            'target',
        )
        read_only_fields = (
            'user',
        )

    def validate_target(self, value):
        """
        1. 이미 팔로우하고 있는 유저인지 확인
        2. 자기 자신을 팔로우하려고 하는지 확인
        """

        if UserFollowRelation.objects.filter(user=self.context['request'].user, target=value).exists():
            raise serializers.ValidationError('이미 팔로우하고 있는 유저입니다.')
        elif self.context['request'].user == value:
            raise serializers.ValidationError('자기 자신을 팔로우할 수 없습니다.')
        return value


class UserFollowRelationSerializer(serializers.ModelSerializer):
    """
    유저 팔로우를 위한 Serializer
    """

    class Meta:
        model = UserFollowRelation
        fields = (
            'pk',
            'user',
            'target',
        )
        read_only_fields = (
            'user',
        )

    def validate_target(self, value):
        """
        1. 이미 팔로우하고 있는 유저인지 확인
        2. 자기 자신을 팔로우하려고 하는지 확인
        """
        print(value)

        if UserFollowRelation.objects.filter(user=self.context['request'].user, target=value).exists():
            raise serializers.ValidationError('이미 팔로우하고 있는 유저입니다.')
        elif self.context['request'].user == value:
            raise serializers.ValidationError('자기 자신을 팔로우할 수 없습니다.')
        return value


class QuestionFollowRelationSerializer(serializers.ModelSerializer):
    """
    질문 팔로우를 위한 Serializer
    """

    class Meta:
        model = QuestionFollowRelation
        fields = (
            'pk',
            'user',
            'question',
        )
        read_only_fields = (
            'user',
        )

    def validate_question(self, value):
        """
        이미 팔로우하고 있는 질문인지 확인
        """

        if QuestionFollowRelation.objects.filter(user=self.context['request'].user, question=value).exists():
            raise serializers.ValidationError('이미 팔로우하고 있는 질문입니다.')
        return value

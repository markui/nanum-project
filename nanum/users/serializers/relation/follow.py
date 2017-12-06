from django.contrib.auth import get_user_model
from rest_framework import serializers

from topics.models import Topic
from users.models import InterestFollowRelation, ExpertiseFollowRelation, UserFollowRelation, QuestionFollowRelation

User = get_user_model()

__all__ = (
    'TopicFollowRelationSerializer',
)


class FollowingTopicSerializer(serializers.ModelSerializer):
    """
    팔로우하는 주제(관심분야/전문분야)을 보여주기 위한 Serializer
    """
    follow_relation_pk = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = (
            'pk',
            'name',
            'image',
            'follow_relation_pk',
        )

    def get_follow_relation_pk(self, obj):
        """
        해당 유저가 팔로우하는 주제 보기를 "요청"한 유저와, 주제의, 팔로우 관계를 나타내는 pk
        해당 페이지에 있는 "주제 팔로우 버튼"이 어떻게 표시되는지를 결정한다
        """
        user = self.context.get('request').user
        if self.context.get('topic_type') == 'interest':
            try:
                topic_follow_relation = obj.interestfollowrelation_set.get(user=user)
            except InterestFollowRelation.DoesNotExist:
                return None
            else:
                return topic_follow_relation.pk
        elif self.context.get('topic_type') == 'expertise':
            try:
                topic_follow_relation = obj.expertisefollowrelation_set.get(user=user)
            except ExpertiseFollowRelation.DoesNotExist:
                return None
            else:
                return topic_follow_relation.pk


class TopicFollowRelationSerializer(serializers.Serializer):
    """
    주제(관심분야/전문분야) 팔로우를 위한 Serializer
    """
    follow_relation_pk = serializers.IntegerField(source='pk', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), required=True)

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

    follow_relation_pk = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = UserFollowRelation
        fields = (
            'follow_relation_pk',
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


class UserFollowParticipantSerializer(serializers.ModelSerializer):
    """
    팔로워/팔로잉 하는 유저 List를 보여주기 위한 Serializer
    """
    thumbnail_image_50 = serializers.SerializerMethodField()
    main_credential = serializers.SerializerMethodField()
    follow_relation_pk = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'pk',
            'name',
            'thumbnail_image_50',
            'main_credential',
            'follow_relation_pk',
        )

    def get_thumbnail_image_50(self, obj):
        # 이미지가 없는 경우, url 속성을 접근하려 할 시 에러가 남
        if not obj.profile.thumbnail_image_50:
            return None
        return obj.profile.thumbnail_image_50.url

    def get_main_credential(self, obj):
        return obj.profile.main_credential

    def get_follow_relation_pk(self, obj):
        """
        해당 팔로워 리스트 보기를 "요청"한 유저와, 팔로워의, 팔로우 관계를 나타내는 pk
        해당 페이지에 있는 "유저 팔로우 버튼"이 어떻게 표시되는지를 결정한다
        """
        try:
            follower_relation = obj.follower_relations.get(user=self.context.get('request').user)
        except UserFollowRelation.DoesNotExist:
            return None
        else:
            return follower_relation.pk


class QuestionFollowRelationSerializer(serializers.ModelSerializer):
    """
    질문 팔로우를 위한 Serializer
    """
    follow_relation_pk = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = QuestionFollowRelation
        fields = (
            'follow_relation_pk',
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

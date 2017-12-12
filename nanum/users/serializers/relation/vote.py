from rest_framework import serializers

from users.models import AnswerUpVoteRelation, AnswerDownVoteRelation

__all__ = (
    'AnswerVoteRelationSerializer',
)


class AnswerVoteRelationSerializer(serializers.ModelSerializer):
    """
    답변 추천을 위한 Serializer
    """

    follow_relation_pk = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = AnswerUpVoteRelation

        fields = (
            'follow_relation_pk',
            'user',
            'answer',
        )
        read_only_fields = (
            'user',
        )

    def validate_answer(self, value):
        """
        이미 추천/비추천한 답변인지 확인
        """
        if self.context['vote_type'] == 'upvote':
            if AnswerUpVoteRelation.objects.filter(user=self.context['request'].user, answer=value).exists():
                raise serializers.ValidationError('이미 추천한 답변입니다.')
            return value
        elif self.context['vote_type'] == 'downvote':
            if AnswerDownVoteRelation.objects.filter(user=self.context['request'].user, answer=value).exists():
                raise serializers.ValidationError('이미 비추천한 답변입니다.')
            return value

    def create(self, validated_data):
        """
        추천/비추천 모두 AnswerVoteRelationSerializer를 공통으로
        사용하게 하기 위해서, APIView에서 어떤 분야인지를 판별해주는,
        self.context['vote_type']을 받아옴
        """
        if self.context['vote_type'] == 'upvote':
            return AnswerUpVoteRelation.objects.create(
                user=validated_data['user'],
                answer=validated_data['answer']
            )

        elif self.context['vote_type'] == 'downvote':
            return AnswerDownVoteRelation.objects.create(
                user=validated_data['user'],
                answer=validated_data['answer']
            )

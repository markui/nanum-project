from rest_framework import serializers

from users.models import AnswerUpVoteRelation, AnswerBookmarkRelation
from ..models import Answer, QuillDeltaOperation
from ..utils.quill_js import QuillJSImageProcessor as img_processor

__all__ = (
    'AnswerPostSerializer',
    'AnswerUpdateSerializer',
    'AnswerGetSerializer',
)


class AnswerPostSerializer(serializers.ModelSerializer):
    content = serializers.JSONField(default=None)

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

    @property
    def request_user(self):
        """
        Request를 보낸 유저를 반환
        :return:
        """
        return self.context['request'].user

    def validate(self, data):
        """
        published가 True인데 content가 비어있을 경우 validation error 를 raise
        :param data:
        :return:
        """
        if not data['content'] and data['published']:
            raise serializers.ValidationError("Content가 없는 답변은 Publish가 불가능합니다.")
        return data

    def save(self, **kwargs):
        """
        Answer 객체를 만들고 content를 AnswerContent로 변환하여 저장
        :param kwargs:
        :return:
        """
        content = self.validated_data.pop('content')
        # request_user를 **kwargs에 추가하여 super().save() 호출
        instance = super().save(user=self.request_user, **kwargs)
        if not content:
            return instance
        delta_list = img_processor.get_delta_operation_list(content, iterator=True)

        # Answer에 대한 content를 Save해주는 함수
        img_processor.save_delta_operation_list(delta_list=delta_list, model=QuillDeltaOperation, post=instance)


class AnswerUpdateSerializer(serializers.ModelSerializer):
    # 해당 유저에 대해서
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


class AnswerGetSerializer(serializers.ModelSerializer):
    user_upvote_relation = serializers.SerializerMethodField()
    user_bookmark_relation = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            'pk',
            'user',
            'question',
            'content',
            'upvote_count',
            'user_upvote_relation',
            'user_bookmark_relation',
            'created_at',
            'modified_at',
        )

    @property
    def request_user(self):
        return self.context['request'].user

    # Relation ManyToMany로 엮인 값들에 대해서 pk를 반환
    def get_user_upvote_relation(self, obj):
        try:
            return AnswerUpVoteRelation.objects.get(user=self.request_user, answer=obj).pk
        except:
            return None

    def get_user_bookmark_relation(self, obj):
        try:
            return AnswerBookmarkRelation.objects.get(user=self.request_user, answer=obj).pk
        except:
            return None

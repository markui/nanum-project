from rest_framework import serializers

from ..models import Answer, QuillDeltaOperation
from ..utils import QuillJSImageProcessor

__all__ = (
    'AnswerSerializer',
    'AnswerUpdateSerializer',
    'AnswerFeedSerializer',
)

img_processor = QuillJSImageProcessor()


class AnswerSerializer(serializers.ModelSerializer):
    content = serializers.JSONField()

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

    def save(self, **kwargs):
        """
        Answer 객체를 만들고 content를 AnswerContent로 변환하여 저장
        :param kwargs:
        :return:
        """
        content = self.validated_data.pop('content')
        instance = super().save(**kwargs)
        delta_list = img_processor.get_delta_operation_list(content, iterator=True)
        # Answer에 대한 content를 Save해주는 함수
        img_processor.save_delta_operation_list(delta_list=delta_list, model=QuillDeltaOperation, post=instance)


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

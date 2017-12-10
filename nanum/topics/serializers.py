from rest_framework import serializers

import utils
from .models import Topic


class TopicSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = Topic
        fields = (
            'pk',
            'creator',
            'name',
            'description',
            'image',
            'answer_count',
            'question_count',
            'created_at',
            'modified_at',
        )
        read_only_fields = (
            'pk',
            'creator',
            'created_at'
            'modified_at',
            'answer_count',
            'question_count',
        )

    def save(self, **kwargs):
        """
        image를 썸네일화 하여 저장
        :param kwargs:
        :return:
        """
        image = self.validated_data.get('image')
        super().save(**kwargs)
        if image:
            resized_image = utils.rescale(data=image.read(), width=200, height=200)
            filename = f"{self.instance.pk}/{image.name}"
            self.instance.image.save(filename, resized_image)

class TopicGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = (
            'pk',
            'creator',
            'name',
            'description',
            'image',
            'answer_count',
            'question_count',
            'expert_count',
            'interest_count',
            'created_at',
            'modified_at',
        )
        read_only_fields = (
            'pk',
            'creator',
            'name',
            'description',
            'image',
            'answer_count',
            'question_count',
            'expert_count',
            'interest_count',
            'created_at',
            'modified_at',
        )

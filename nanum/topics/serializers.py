from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.fields import ImageField

import utils
from .models import Topic


# from rest_framework.fields import ImageField


class TopicSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=False)
    image = ImageField(max_length=None, allow_empty_file=False, use_url=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        method = self.context.get('request').method
        if method == 'POST':
            self.fields['name'] = serializers.CharField(max_length=100, required=True)

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
            'created_at'
            'modified_at',
            'answer_count',
            'question_count',
            'expert_count',
            'interest_count',
        )

    def validate_name(self, value):
        topic = Topic.objects.filter(name=value)
        if topic:
            raise ParseError({"error": "이미 존재하는 Topic 이름입니다."})
        return value

    def save(self, **kwargs):
        """
        image를 썸네일화 하여 저장
        :param kwargs:
        :return:
        """
        image = self.validated_data.pop('image', None)
        if not image:
            return super().save(**kwargs)

        with atomic():
            try:
                super().save(**kwargs)
                resized_image = utils.rescale(data=image.read(), width=200, height=200)
                filename = f"{self.instance.pk}/{image.name}"
                self.instance.image.save(filename, resized_image, save=False)
            except:
                raise ParseError({"error": "이미지 저장에 실패했습니다."})


class TopicGetSerializer(serializers.ModelSerializer):
    image = ImageField(max_length=None, allow_empty_file=False, use_url=False)

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

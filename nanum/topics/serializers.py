from rest_framework import serializers

from .models import Topic


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = (
            'pk',
            'creator',
            'name',
            'questions',
            'description',
            'image',
            'created_at'
        )

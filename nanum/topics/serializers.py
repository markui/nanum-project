from rest_framework import serializers

from .models import Topic


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = (
            'pk',
            'creator',
            'name',
            'description',
            'image',
            'created_at'
        )

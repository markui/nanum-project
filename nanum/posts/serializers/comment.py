from rest_framework import serializers

from ..models import Comment

__all__ = (
    'CommentSerializer',
)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'pk',
            'user',
            'content',
            'parent',
            'post_manager',
            'created_at',
            'modified_at',
        )

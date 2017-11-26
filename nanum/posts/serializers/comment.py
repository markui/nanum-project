from rest_framework import serializers

from ..models import Comment, PostType

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
            'created_at',
            'modified_at',
            'parent',
            'post_type',
        )

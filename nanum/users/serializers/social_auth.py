from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class FacebookLoginSerializer(serializers.Serializer):
    """
    페이스북 로그인을 위한 Serializer
    """
    access_token = serializers.CharField(write_only=True)
    facebook_user_id = serializers.CharField(write_only=True)


class FacebookUserSerializer(serializers.ModelSerializer):
    """
    facebook 유저 정보를 보여주기 위한 Serializer
    """
    thumbnail_image_25 = serializers.ImageField(source='profile.thumbnail_image_25')
    thumbnail_image_50 = serializers.ImageField(source='profile.thumbnail_image_50')

    class Meta:
        model = User
        fields = (
            'pk',
            'name',
            'thumbnail_image_25',
            'thumbnail_image_50',
        )

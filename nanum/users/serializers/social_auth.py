from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class FacebookLoginSerializer(serializers.Serializer):
    """
    페이스북 로그인을 위한 Serializer
    """
    access_token = serializers.CharField(write_only=True)
    facebook_user_id = serializers.CharField(write_only=True)

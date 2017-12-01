from django.contrib.auth import get_user_model
from rest_framework import serializers

from topics.models import Topic
from users.models import InterestFollowRelation

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    """
    이메일 회원가입을 위한 Serializer
    """
    email = serializers.EmailField(max_length=254)
    password1 = serializers.CharField(write_only=True, max_length=128)
    password2 = serializers.CharField(write_only=True, max_length=128)

    class Meta:
        model = User
        fields = (
            'email',
            'name',
            'password1',
            'password2',
        )

    def validate_email(self, value):
        """
        이미 존재하는 유저 이메일인지 확인
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('해당 이메일로 가입된 계정이 이미 존재합니다.')
        return value

    def validate(self, data):
        """
        password1, password2가 일치하는지 확인
        """
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('비밀번호가 일치하지 않습니다')
        print(data)
        return data

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password1'],
            user_type='EM',
        )

    def to_representation(self, instance):
        # serialize 될 형태를 결정
        # token과 User info를 분리하여
        # 클라이언트에게 전달
        ret = super().to_representation(instance)
        data = {
            'user': ret,
            'token': instance.token,
        }
        # 마지막에는 serializer.data를 출력했을 때 반환될 값을 반환해줘야 함
        return data


class LoginSerializer(serializers.ModelSerializer):
    """
    이메일 로그인을 위한 Serializer
    """
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
        )


class FacebookLoginSerializer(serializers.Serializer):
    """
    페이스북 로그인을 위한 Serializer
    """
    access_token = serializers.CharField(write_only=True)
    facebook_user_id = serializers.CharField(write_only=True)


class TopicFollowRelationSerializer(serializers.Serializer):
    """
    주제(관심분야/전문분야) 팔로우를 위한 Serializer
    """

    class Meta:
        model = InterestFollowRelation
        fields = (
            'user'
            'topic'
        )
        read_only_fields = (
            'user'
        )

    def validate_topic(self, value):
        """
        실제 존재하는 topic pk인지 확인
        """
        if not Topic.objects.filter(pk=value).exists():
            raise serializers.ValidationError('존재하지 않는 주제입니다.')
        elif self.Meta.model.objects.filter(user=self.context['request'].user, topic=value):
            raise serializers.ValidationError('이미 팔로우하고 있는 주제입니다.')
        else:
            return value


class TopicFollowRelationDetailSerializer(serializers.Serializer):
    pass

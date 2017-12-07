from django.contrib.auth import get_user_model
from rest_framework import serializers

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

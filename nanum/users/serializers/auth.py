from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class EmailUserSerializer(serializers.ModelSerializer):
    """
    이메일 유저 정보를 보여주기 위한 Serializer
    """
    thumbnail_image_25 = serializers.ImageField(source='profile.thumbnail_image_25')
    thumbnail_image_50 = serializers.ImageField(source='profile.thumbnail_image_50')

    class Meta:
        model = User
        fields = (
            'pk',
            'email',
            'name',
            'thumbnail_image_25',
            'thumbnail_image_50',
        )


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
            'pk',
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
        # ret = super().to_representation(instance)
        data = {
            'user': EmailUserSerializer(instance).data,
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


class PasswordResetSendMailSerializer(serializers.Serializer):
    """
    비밀번호 재설성 링크를 담은 이메일을 보낼 <user input email> 을
    받는 Serializer
    """
    email = serializers.EmailField(max_length=254)

    def validate_email(self, value):
        """
        존재하는 이메일 유저인지 확인하기
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('해당 이메일로 가입된 계정이 존재하지 않습니다')
        else:
            return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    비밀번호 재설성 링크에 담긴 유저의 암호화된 pk + 토큰 을 받고,
    복호화된 pk + 토큰을 돌려주는
    Serializer
    """
    code = serializers.CharField(write_only=True)
    uid = serializers.CharField(write_only=True)



class PasswordResetSerializer(serializers.Serializer):
    """
    비밀번호 재설정을 위한 Serializer
    """
    pk = serializers.IntegerField(write_only=True)
    token = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True, max_length=128)
    password2 = serializers.CharField(write_only=True, max_length=128)

    def validate(self, data):
        """
        1. password1, password2가 일치하는지 확인
        2. 올바른 토큰 + pk 인지 확인
           - 실제 존재하는 토큰인지
           - 토큰의 유저 pk와 전달된 pk가 일치하는지
        """
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('비밀번호가 일치하지 않습니다')
        try:
            token = Token.objects.get(key=data['token'])
        except Token.DoesNotExist:
            raise serializers.ValidationError('해당 토큰을 가진 유저가 존재하지 않습니다')
        else:
            if token.user.pk != data['pk']:
                raise serializers.ValidationError('해당 토큰을 가진 유저의 pk와 전달된 pk가 일치하지 않습니다')
            data.update({'token_model': token})
            return data


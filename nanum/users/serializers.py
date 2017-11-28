from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'name',
            'password1',
            'password2',
        )



    def validate(self, data):
        """
        password1, password2가 일치하는지 확인
        """



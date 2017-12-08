from rest_framework import serializers

from users.models import Profile, UserFollowRelation


class ProfileSerializer(serializers.ModelSerializer):
    """
    프로필 정보 가져오기/업데이트를 위한 Serializer

    update 시에는 일반 'image'를 업로드
    retrieve 시에는 200*200 사이즈의 'thumbnail_image_200' 가져오기
    """
    name = serializers.CharField(source='user.name', max_length=30)
    follow_relation_pk = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True)

    class Meta:
        model = Profile
        fields = (
            'image',
            'thumbnail_image_200',
            'name',
            'main_credential',
            'description',
            'follow_relation_pk',
        )
        read_only_fields = (
            'thumbnail_image_200',
        )

    def get_follow_relation_pk(self, obj):
        """
        해당 유저의 프로필 보기를 "요청"한 유저와, 프로필의 유저의, 팔로우 관계를 나타내는 pk
        해당 페이지에 있는 "유저 팔로우 버튼"이 어떻게 표시되는지를 결정한다
        """
        user = self.context.get('request').user
        try:
            user_follow_relation = user.following_relations.get(target=obj.user.pk)
        except UserFollowRelation.DoesNotExist:
            return None
        else:
            return user_follow_relation.pk

    def update(self, instance, validated_data):
        """
        프로필 업데이트
        - name의 경우는 유저 모델에 속하므로 유저 모델에 name 값을 추가한 뒤 저장한다
        :param Profile object instance:
        :param validated_data:
        :return:
        """
        instance.main_credential = validated_data.get('main_credential', instance.main_credential)
        instance.description = validated_data.get('description', instance.description)
        if validated_data.get('user'):
            # 유저 name이 올 경우, name을 유저 모델에 저장
            instance.user.name = validated_data.get('user').get('name')
            instance.user.save()
        # 이미지가 새로 업로드된 경우,
        if validated_data.get('image'):
            instance.image = validated_data.get('image')
            instance.save()
        # 이미지가 업로드되지 않은 경우
        else:
            instance.save(status='same-image')

        return instance

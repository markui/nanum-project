from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from topics.models import Topic
from users.models import Profile, UserFollowRelation, EmploymentCredential, EducationCredential
from users.utils import ParameterisedHyperlinkedIdentityField
from users.utils.fields import DefaultStaticImageSerializerField


class ProfileSerializer(serializers.ModelSerializer):
    """
    프로필 main-detail 가져오기/업데이트를 위한 Serializer

    update 시에는 일반 'image'를 업로드
    retrieve 시에는 200*200 사이즈의 'thumbnail_image_200' 가져오기
    """
    name = serializers.CharField(source='user.name', max_length=30)
    follow_relation_pk = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True)
    thumbnail_image_200 = DefaultStaticImageSerializerField(read_only=True)

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

    def get_follow_relation_pk(self, obj):
        """
        해당 유저의 프로필 보기를 "요청"한 유저와, 프로필의 유저의, 팔로우 관계를 나타내는 pk
        해당 페이지에 있는 "유저 팔로우 버튼"이 어떻게 표시되는지를 결정한다
        """
        user = self.context.get('request').user
        if user.is_authenticated():
            try:
                user_follow_relation = user.following_relations.get(target=obj.user.pk)
            except UserFollowRelation.DoesNotExist:
                return None
            else:
                return user_follow_relation.pk
        else:
            return None
    #
    # def get_thumbnail_image_200(self, obj):
    #     return obj.thumbnail_image_200.url

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


class ProfileStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'answer_count',
            'upvote_count',
            'follower_count',
            'following_count',
        )


class TopicSerializer(serializers.ModelSerializer):
    """
    프로필 경력의, 회사(주제)
    프로필 학력의, 학교(주제), 전공(주제)을
    Nested Serializer로 보여줄 때 활용할 Model Serializer
    """

    class Meta:
        model = Topic
        fields = ('pk', 'name', 'image')


class EmploymentCredentialSerializer(serializers.ModelSerializer):
    """
    프로필 경력 정보 Serializer
    """
    url = ParameterisedHyperlinkedIdentityField(view_name="user:profile-empl-credential-detail", lookup_fields=(
        ('profile.user.pk', 'pk'), ('pk', 'credential_pk')), read_only=True)
    company = TopicSerializer(read_only=True)
    company_id = serializers.IntegerField(write_only=True, required=False)
    type = serializers.SerializerMethodField()

    class Meta:
        model = EmploymentCredential
        fields = (
            'pk',
            'url',
            'company',
            'company_id',
            'position',
            'start_year',
            'end_year',
            'working_status',
            'type',
        )

    def get_type(self, obj):
        return 'empl'

    def validate(self, data):
        """
        1. 회사 pk나 직위 모두 입력하지 않은 경우, 에러 발생
        2. end_year가 start_year보다 앞선 경우, 에러 발생
        :param data: validated_data
        :return:
        """
        if not data.get('company') and not data.get('position'):
            raise ValidationError({
                'error': '회사나 직위 중 적어도 하나의 정보를 입력해주세요.'
            })
        start_year = data.get('start_year')
        end_year = data.get('end_year')
        if start_year and end_year:
            if start_year > end_year:
                raise ValidationError({
                    'error': '입사년도가 퇴사년도보다 늦습니다.'
                })
        return data


class EducationCredentialSerializer(serializers.ModelSerializer):
    """
    프로필 학력 정보 Serializer
    """
    url = ParameterisedHyperlinkedIdentityField(view_name="user:profile-edu-credential-detail", lookup_fields=(
        ('profile.user.pk', 'pk'), ('pk', 'credential_pk')), read_only=True)
    type = serializers.SerializerMethodField()

    school = TopicSerializer(read_only=True)
    school_id = serializers.IntegerField(write_only=True, required=False)
    concentration = TopicSerializer(read_only=True)
    concentration_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = EducationCredential
        fields = (
            'pk',
            'url',
            'school',
            'school_id',
            'concentration',
            'concentration_id',
            'degree_type',
            'graduation_year',
            'type',
        )

    def get_type(self, obj):
        return 'edu'

    def validate(self, data):
        """
        학교 pk나 전공 pk 모두 입력하지 않은 경우, 에러 발생
        :param data: validated_data
        :return:
        """
        if not data.get('school_id') and not data.get('concentration_id'):
            raise ValidationError({
                'error': '학교나 전공 중 적어도 하나의 정보를 입력해주세요.'
            })

        return data

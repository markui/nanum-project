import base64
import json
import os
import random
import re
import string
from collections import OrderedDict
from io import BytesIO

from PIL import Image as pil
from django.conf import settings
from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.db.transaction import atomic

__all__ = (
    'QuillJSDeltaParser',
)


class QuillJSDeltaParser:
    """
    QuillJSDelta가 저장되는 model과 ForeignKey로 연결되어있는 parent_model을 Parsing 해주는 Class
    """

    def __init__(self, model=None, parent_model=None):
        self.model = model
        self.parent_model = parent_model

        self._validate()

    def _validate(self):
        self._validate_django_model()
        self._validate_model_fields()
        self._validate_line_no_in_model()

    def _validate_django_model(self):
        """
        model과 parent_model이 Django 모델인지 확인
        :return:
        """
        assert type(self.model) == ModelBase, "Initialized model is not an instance of Django's ModelBase."
        assert type(
            self.parent_model) == ModelBase, "Initialized parent model is not an instance of Django's ModelBase."

    def _validate_model_fields(self):
        """
        model이 parent_model에 ForeignKey 관계를 갖는지 확인
        :return:
        """
        foreignkey_field = self._get_related_field()
        if not foreignkey_field:
            raise AttributeError("self.model and self.parent_model are not related.")

    def _validate_line_no_in_model(self):
        """
        model에 line_no 라는 이름의 필드가 존재하는지 확인하며 Integer필드인지 확인
        :return:
        """
        field_names = [field.name for field in self.model._meta.fields]
        if "line_no" not in field_names:
            raise AttributeError("line_no not in self.model")

    def _get_related_field(self):
        """
        model과 parent_model의 ForeignKey의 이름을 반환
        :return: foreign_field.name - string
        """
        foreignkey_fields = iter([field for field in self.model._meta.fields if field.many_to_one])
        for foreignkey_field in foreignkey_fields:
            if isinstance(foreignkey_field.related_model, type(self.parent_model)):
                return foreignkey_field.name

    @classmethod
    def get_delta_operation_list(cls, delta: dict, iterator: bool = False):
        """
        Delta 내부에 있는 Opertaion의 list를 반환
        {"ops":[{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}]}
        ->
        ([{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}])

        :param delta: Dict - QuillJS content 정보
        :param iterator: Boolean - True면 iterator 반환, False면 일반 list 반환

        :return:
        """
        assert type(delta) == dict, "Delta is not dict. Check if is JSON."
        assert 'ops' in delta.keys(), "Ops not in delta."

        if iterator:
            return iter(delta['ops'])
        return delta['ops']

    @classmethod
    def create_quill_content(cls, delta_operation_list: list, json: bool = False):
        """
        [{'insert':{'image':'data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=='}},{'insert":'\n'}]
        ->
        {"ops":[{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}]}
        json boolean 값을 통해 dictionary, 혹은 json화된 byte 형태의 string을 반환
        :param content:

        :return:
        """
        assert type(delta_operation_list) == list, "Delta Operation List is not type List."

        content = OrderedDict()
        content['ops'] = delta_operation_list
        if json:
            return json.dumps(content)
        return content

    def save_delta_operation_list(self, content, parent_instance):
        """
        self.model에 대해 bulk_create를 통해 content를 저장

        :param content: Content의 정보가 들은 delta안의 list
        :param instance: 위 모델에 연결될 Foreignkey 모델의 Instance, parent_model의 Instance

        :return: 반환값은 없으며 bulk_create와 이미지 삭제 함수를 실행
        """
        # Instance가 parent_model의 instance인지 확인
        assert type(parent_instance) == self.parent_model, "Instance is not an instance of parent model."

        # Bulk Create할 instance를 모아둘 list instantiation
        # get_delta_operation_list를 통해 content에서 delta operation이 담긴 list 반환
        instances_to_bulk_create = list()
        delta_list = self.get_delta_operation_list(content, iterator=True)

        # delta_list 내에 있는 quill_delta_operation에 대해 self.model을 instantiate
        for line_no, quill_delta_operation in enumerate(delta_list, start=1):
            model_instance = self._instantiate_model(
                quill_delta_operation=quill_delta_operation,
                line_no=line_no,
                parent_instance=parent_instance
            )

            # 이미지에 문제가 있어 self.model의 instance가 생성되지 않았을 경우
            if type(model_instance) != self.model:
                return None
            instances_to_bulk_create.append(model_instance)

        # django의 bulk_create를 통해 전달된 model의 instance들을 한꺼번에 생성, 생성된 이미지 파일들을 삭제
        return self.model.objects.bulk_create(instances_to_bulk_create)
        # self._delete_temporary_images(images_to_delete)

    def _instantiate_model(self, quill_delta_operation, line_no, parent_instance):
        """
        kwargs 를 만들어 _instantiate에 전달

        :param quill_delta_operation:
        :param line_no:
        :param instance:
        :return:
        """
        insert_value = quill_delta_operation.get('insert')
        attributes = quill_delta_operation.get('attributes')

        # 필드 이름을 갖고와서
        field_name = self._get_related_field()
        kwargs = {
            "insert_value": insert_value,
            "attributes_value": attributes,
            "line_no": line_no,
            field_name: parent_instance
        }

        return self._instantiate(**kwargs)

    def _instantiate(self, insert_value, **kwargs):
        """
        model 을 text 혹은 image로 나누어 instance를 만듬

        :param insert_value: Delta Operation 의 insert key에 대한 value.
                    text 혹은 {"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}
        :param **kwargs:
                - attributes_value: (None or attribute from insert),
                - line_no: 해당 delta operation이 있었던 줄 번호
                - ForeignKey Field name: instance
        :return: self.model 에 대한 객체
        """
        # Attribute, line_no, Foreignkey field 를 기반으로 model object를 일단 instantiate
        instance = self.model(**kwargs)

        # insert 안에 image가 있을 경우
        # image 가 base64인 경우 instance에 이미지 추가
        try:
            image_value = insert_value.get('image')
            try:
                decoded_data = self._parse_base64(image_base64=image_value)
                filename = self._generate_filename(format=format, **kwargs)
                image = self._image_process(data=decoded_data, max_size=600)

                instance.image.save(
                    filename,
                    image,
                    save=False
                )
                instance.image_insert_value = {"image": f"{instance.image.url}"}

            # image 가 base64가 아닌 경우
            # url 주소일 경유 담겨있을 경우 image_insert_value에 url 추가
            # image 가 base64도 아니고 link도 아닌 잘못된 형식일 경우
            except AttributeError:
                if image_value[:4] == "http" or image_value[:6] == settings.MEDIA_URL:
                    instance.image_insert_value = {"image": f"{image_value}"}
                else:
                    raise ValueError("올바른 형태의 이미지가 아닙니다.")

        # insert 안에 Text만 있을 경우
        except AttributeError:
            instance.insert_value = insert_value
        return instance

    def _parse_base64(self, image_base64):
        """
        Base64 형태의 image를 받아서 이미지 format과 decoded_data를 분리해서 반환
        :param image_base64: base64 형태의 이미지 데이터 string
        :return:
        """
        data = re.match(r'\w+:image\/\w+;\w+,(.+)', image_base64)

        # 정규표현식으로 매치된 이미지 저장 포맷과 이미지 데이터를 나눔
        byte_data_string = data.group(1)

        # image_data_string 파싱에 실패 했을 경우
        if not byte_data_string:
            raise AttributeError

        byte_data_base64 = bytes(byte_data_string, 'utf-8')
        decoded_data = base64.b64decode(byte_data_base64)
        return decoded_data

    def _generate_filename(self, format, **kwargs) -> string:
        """
        이미지 파일 이름 생성

        :param format: 파일 형태 format
        :return:
        """
        fk_field_name = self._get_related_field()
        fk_field_instance = kwargs.get(fk_field_name)

        # Create filename
        rand_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        filename = f'{fk_field_name}-{fk_field_instance.pk}__{rand_str}.jpeg'

        return filename

    def _image_process(self, data: base64, max_size: int):
        """
        base64 이미지 데이터를 받아 height, width 중 긴 쪽을 max_size에 맞추고 다른 쪽을 Ratio에 따라 줄여서 jpeg형식으로 반환

        :param data:
        :return:
        """
        original_img = BytesIO(data)
        img = pil.open(original_img)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        src_width, src_height = img.size
        gtr_side = max(src_width, src_height)
        ratio = float(max_size) / float(gtr_side)

        # 이미지의 가로 혹은 이미지의 세로가 max_size보다 작을 경우
        # 긴 쪽을 max_size에 맞추고 짧은 쪽을 max_size * ratio
        # 새 width 와 height를 통해 resize
        if src_width > max_size or src_height > max_size:
            if src_width > src_height:
                dst_width = max_size
                dst_height = int(src_height * ratio)
            else:
                dst_height = max_size
                dst_width = int(src_width * ratio)
            img = img.resize((dst_width, dst_height), pil.ANTIALIAS)

        output_img = BytesIO()
        img.save(output_img, 'JPEG')

        return output_img

    def update_delta_operation_list(self, queryset: QuerySet,
                                    content: dict, parent_instance):
        """
        전달받은 model에 대해 update, delete create을 실행

        :param queryset: Quill Operation 이 담겨있는 Queryset
        :param content: request.data의 content
        :param parent_instance: Quill Operation 와 ForeignKey로 연결되는 parent_instance
        :return:
        """
        assert type(queryset[0]) == self.model
        assert type(parent_instance) == self.parent_model

        # Queryset 에서 {Quill operation : instance, ...} 형식의 dict 생성
        # Quill operation 은 json dumps를 통한 string 형태
        operation_instance_dict = {
            json.dumps(qdo_instance.delta_operation): qdo_instance
            for qdo_instance
            in queryset
        }

        # Request.data.content 에서 {Quill operation : line_number, ...} 형식의 dict 생성
        # Quill operation 은 json dumps를 통한 string 형태
        operation_lineno_dict = {
            json.dumps(qdo): line_no
            for line_no, qdo
            in enumerate(self.get_delta_operation_list(content, iterator=True), start=1)
        }

        # 델타 줄의 string들에 대해서 set operation을 실행,
        # to_update: 같은 내용의 경우, line number를 update 해야 되는 내용
        # to_create: 새로운 내용일 경우, 새 instance를 create 해야 되는 내용
        # to_delete: 지워야 하는 내용일 경우, 지워진 내용
        instance_delta_set = set(operation_instance_dict.keys())
        request_delta_set = set(operation_lineno_dict.keys())
        to_update = instance_delta_set & request_delta_set
        to_create = request_delta_set - instance_delta_set
        to_delete = instance_delta_set - request_delta_set

        self._bulk_update_instance(
            to_update=to_update,
            operation_lineno_dict=operation_lineno_dict,
            operation_instance_dict=operation_instance_dict
        )
        self._bulk_create_instance(
            to_create=to_create,
            operation_lineno_dict=operation_lineno_dict,
            parent_instance=parent_instance
        )
        self._bulk_delete_instance(
            to_delete=to_delete,
            operation_instance_dict=operation_instance_dict
        )

    @atomic
    def _bulk_update_instance(self, to_update, operation_lineno_dict, operation_instance_dict):
        """

        :param to_update:
        :param operation_lineno_dict:
        :param operation_instance_dict:
        :return:
        """
        # update
        # replace instance line_no with request line_no
        for delta_operation in to_update:
            new_line_no = operation_lineno_dict[delta_operation]
            dt_instance = operation_instance_dict[delta_operation]

            dt_instance.line_no = new_line_no
            dt_instance.save()

    @atomic
    def _bulk_create_instance(self, to_create, operation_lineno_dict, parent_instance):
        """

        :param to_create:
        :param operation_lineno_dict:
        :param instance:
        :return:
        """
        # create
        # create instance with request line_no
        instances_to_bulk_create = list()
        for delta_operation_str in to_create:
            # Get line_no
            line_no = operation_lineno_dict[delta_operation_str]

            # Get delta_operation
            quill_delta_operation = json.loads(json.loads((json.dumps(delta_operation_str))))

            # instantiate model for bulk create
            object = self._instantiate_model(
                quill_delta_operation=quill_delta_operation,
                line_no=line_no,
                parent_instance=parent_instance
            )
            instances_to_bulk_create.append(object)

        self.model.objects.bulk_create(instances_to_bulk_create)

    @atomic
    def _bulk_delete_instance(self, to_delete, operation_instance_dict):
        """

        :param to_delete:
        :param operation_instance_dict:
        :return:
        """
        # delete
        # delete instance with delta op value
        for delta_operation in to_delete:
            instance = operation_instance_dict[delta_operation]
            instance.delete()

    def _delete_temporary_images(self, *args, **kwargs):
        """
        Deprecated

        :param list:
        :return:
        """
        assert (len(kwargs) + len(args)) < 2, "Only one keyword argument accepted"
        data = args[0] if args else list(kwargs.keys())[0]
        try:
            # 내부에 생성되었던 Image 파일들을 삭제
            for imagefile in data:
                os.remove(imagefile)
        except:
            os.remove(data)

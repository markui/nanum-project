import base64
import json
import os
import random
import re
import string
from collections import OrderedDict

from django.db.models.base import ModelBase
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
        assert type(self.model) == ModelBase, "Initialized model is not an instance of Django's ModelBase."
        assert type(
            self.parent_model) == ModelBase, "Initialized parent model is not an instance of Django's ModelBase."

    def _validate_model_fields(self):
        foreign_fields = iter([field for field in self.model._meta.fields if field.many_to_one])
        for foreign_field in foreign_fields:
            if isinstance(foreign_field.related_model, type(self.parent_model)):
                return
        raise AttributeError("self.model and self.parent_model are not related.")

    def _validate_line_no_in_model(self):
        field_names = [field.name for field in self.model._meta.fields]
        if "line_no" not in field_names:
            raise AttributeError("line_no not in self.model")

    def _get_related_field(self):
        foreign_fields = iter([field for field in self.model._meta.fields if field.many_to_one])
        for foreign_field in foreign_fields:
            if isinstance(foreign_field.related_model, type(self.parent_model)):
                return foreign_field.name

    @classmethod
    def get_quill_content(cls, content: json):
        """
        Request에서 content부분(type = JSON)을 뽑아내 dict을 만듬
        {'content':{"ops":[{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}]}}
        ->
        {"ops":[{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}]}
        :param content: JSON - 클라이언트에서 POST를 통해 받은 JSON형태의 request data
        :return: Dict 형태의 QuillJS content 정보
        """
        return json.loads(content)

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
        json boolean 값을 통해 dictionary를 반환받을지 json화된 byte 형태의 string을 반환받을지를 결정
        :param content:
        :return:
        """
        content = OrderedDict()
        content['ops'] = delta_operation_list
        if json:
            return json.dumps(content)
        return content

    def save_delta_operation_list(self, content, instance):
        """
        self.model에 대해 bulk_create를 통해 content를 저장

        :param content: Content의 정보가 들은 delta안의 list
        :param **kwargs:
                - instance: 위 모델에 연결될 Foreignkey 모델 Instance

        :return: 반환값은 없으며 bulk_create와 이미지 삭제 함수를 실행
        """
        # Instance가 parent_model의 instance인지 확인
        assert type(instance) == self.parent_model, "Instance is not an instance of parent model."

        # Bulk Create할 instance와 지울 images들을 미리 list로 instantiate
        # Content를 delta operation이 담긴 list로 정제
        instances_to_bulk_create, images_to_delete = list(), list()
        delta_list = self.get_delta_operation_list(content, iterator=True)

        # delta_list 내에 있는 quill_delta_operation에 대해 self.model을 instantiate
        for line_no, quill_delta_operation in enumerate(delta_list, start=1):
            object = self._instantiate_model(
                quill_delta_operation=quill_delta_operation,
                line_no=line_no,
                instance=instance
            )
            instances_to_bulk_create.append(object)
            if object.image:
                images_to_delete.append(object.image.name)

        # django의 bulk_create를 통해 전달된 model의 instance들을 한꺼번에 생성, 생성된 이미지 파일들을 삭제
        self.model.objects.bulk_create(instances_to_bulk_create)
        self._delete_temporary_images(images_to_delete)

    def _instantiate_model(self, quill_delta_operation, line_no, instance):
        """
        kwargs 를 만들어 _instantiate에 전달
        :param quill_delta_operation:
        :param line_no:
        :param instance:
        :return:
        """
        insert_value = quill_delta_operation.get('insert')
        attributes = quill_delta_operation.get('attributes')
        field_name = self._get_related_field()
        kwargs = {
            "insert_value": insert_value,
            "attributes_value": attributes,
            "line_no": line_no,
            field_name: instance
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
                -
        :return: self.model 에 대한 객체
        """
        object = self.model(**kwargs)

        # extract image from insert if exists
        try:
            image_data_string = insert_value['image']

            # check if the value is not already a url
            if image_data_string[:4] == "data":
                image_type, decoded_data = self._split_image_base64(
                    image_data_string=image_data_string
                )
                filename = self._save_image(
                    image_type=image_type,
                    decoded_data=decoded_data,
                    **kwargs
                )
                object.image = filename
                object.image.save(filename, object.image, save=False)
                object.image_insert_value = {"image": f"{object.image.url}"}

        except:  # else insert is text and return class instance with insert as text value, with and attribute(or None)
            object.insert_value = insert_value

        return object

    def _split_image_base64(self, image_data_string):
        """
        Base64 형태의 image를 받아서 image_type과 decoded_data를 분리해서 반환
        :param image_data_string:
        :return:
        """
        data = re.match(r'\w+:image\/(\w+);\w+,(.+)', image_data_string)
        image_type = data.group(1)
        byte_data_string = data.group(2)
        byte_data_base64 = bytes(byte_data_string, 'utf-8')
        decoded_data = base64.b64decode(byte_data_base64)
        return image_type, decoded_data

    def _save_image(self, image_type, decoded_data, answer, **kwargs) -> string:
        """
        이미지를 프로젝트 폴더 자체에 생성
        :param image_type:
        :param decoded_data:
        :param post:
        :param classname:
        :return:
        """
        # Create filename
        rand_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        filename = f'a-{answer.pk}__{rand_str}.{image_type}'
        self._save_temporary_image(filename, decoded_data)
        return filename

    def _save_temporary_image(self, filename, decoded_data):
        """
        추후 Async로 변경

        :param filename:
        :param decoded_data:
        :return:
        """
        with open(filename, 'wb') as f:
            f.write(decoded_data)
            f.close()

    def _delete_temporary_images(self, *args, **kwargs):
        """
        추후 Async로 변경

        :param list:
        :return:
        """
        assert (len(kwargs) + len(args) < 2, "Only one keyword argument accepted")
        data = args[0] if args else list(kwargs.keys())[0]
        try:
            # 내부에 생성되었던 Image 파일들을 삭제
            for imagefile in data:
                os.remove(imagefile)
        except:
            os.remove(data)

    def update_delta_operation_list(self, queryset, content, instance):
        """
        전달받은 model에 대해 update, delete create을 실행

        :param queryset:
        :param content:
        :param model:
        :param kwargs:
        :return:
        """
        # Create a dict of quill operation(string) : instance from queryset
        instance_delta_instance_dict = {
            json.dumps(qdo_instance.delta_operation): qdo_instance
            for qdo_instance
            in queryset
        }

        # Create a dict of quill operations(string) : line_number from request.data.content
        request_delta_line_no_dict = {
            json.dumps(qdo): line_no
            for line_no, qdo
            in enumerate(self.get_delta_operation_list(content, iterator=True), start=1)
        }

        # 델타 줄의 string들에 대해서 set operation을 실행,
        # to_update: 같은 내용의 경우, line number를 update 해야 되는 내용
        # to_create: 새로운 내용일 경우, 새 instance를 create 해야 되는 내용
        # to_delete: 지워야 하는 내용일 경우, 지워진 내용
        instance_delta_set = set(instance_delta_instance_dict.keys())
        request_delta_set = set(request_delta_line_no_dict.keys())
        to_update = instance_delta_set & request_delta_set
        to_create = request_delta_set - instance_delta_set
        to_delete = instance_delta_set - request_delta_set

        self._bulk_update_instance(
            to_update=to_update,
            request_delta_line_no_dict=request_delta_line_no_dict,
            instance_delta_instance_dict=instance_delta_instance_dict
        )
        self._bulk_create_instance(
            to_create=to_create,
            request_delta_line_no_dict=request_delta_line_no_dict,
            instance=instance
        )
        self._bulk_delete_instance(
            to_delete=to_delete,
            instance_delta_instance_dict=instance_delta_instance_dict
        )

    @atomic
    def _bulk_update_instance(self, to_update, request_delta_line_no_dict, instance_delta_instance_dict):
        """

        :param to_update:
        :param request_delta_line_no_dict:
        :param instance_delta_instance_dict:
        :return:
        """
        # update
        # replace instance line_no with request line_no
        for delta_operation in to_update:
            new_line_no = request_delta_line_no_dict[delta_operation]
            dt_instance = instance_delta_instance_dict[delta_operation]
            dt_instance.line_no = new_line_no
            dt_instance.save()

    @atomic
    def _bulk_create_instance(self, to_create, request_delta_line_no_dict, instance):
        """

        :param to_create:
        :param request_delta_line_no_dict:
        :param instance:
        :return:
        """
        # create
        # create instance with request line_no
        instances_to_bulk_create = list()
        for delta_operation_str in to_create:
            # Get line_no
            line_no = request_delta_line_no_dict[delta_operation_str]

            # Get delta_operation
            quill_delta_operation = json.loads(json.loads((json.dumps(delta_operation_str))))

            # instantiate model for bulk create
            object = self._instantiate_model(
                quill_delta_operation=quill_delta_operation,
                line_no=line_no,
                instance=instance
            )
            instances_to_bulk_create.append(object)
        self.model.objects.bulk_create(instances_to_bulk_create)

    @atomic
    def _bulk_delete_instance(self, to_delete, instance_delta_instance_dict):
        """

        :param to_delete:
        :param instance_delta_instance_dict:
        :return:
        """
        # delete
        # delete instance with delta op value
        for delta_operation in to_delete:
            instance = instance_delta_instance_dict[delta_operation]
            instance.delete()

    @classmethod
    def delete_image_file(cls, *args):
        """
        Takes a single string of the name of the image or list of strings as args.
        If List, iterate through to delete the files in the list.
        If String, delete the single file.
        :param args:
        :return:
        """
        pass

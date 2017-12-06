import base64
import json
import os
import random
import re
import string
from collections import OrderedDict

from django.db.transaction import atomic

__all__ = (
    'QuillJSImageProcessor',
)


class QuillJSImageProcessor:
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

    @classmethod
    def save_delta_operation_list(cls, content, model, **kwargs):
        """
        전달받은 model변수에 해당하는 Django 모델명에 대해 bulk_create를 통해 content를 저장

        :param delta_list: Content의 정보가 들은 delta안의 list
        :param model: Quill JS의 한 Operation이 저장될 Django의 모델
        :param **kwargs:
                - post: 위 모델에 연결될 Foreignkey 모델 Instance

        :return: 반환값은 없으며 bulk_create와 이미지 삭제 함수를 실행
        """

        delta_list = cls.get_delta_operation_list(content, iterator=True)

        instances_to_bulk_create = []
        images_to_delete = []
        # Delta List를 순회할 때 line_no 를 추가
        for line_no, quill_delta_operation in enumerate(delta_list, start=1):
            insert_value, attributes = quill_delta_operation['insert'], \
                                       quill_delta_operation.get('attributes', None)

            object = cls._instantiate_model(
                insert_value=insert_value,
                model=model,
                attributes_value=attributes,
                line_no=line_no,
                **kwargs
            )
            instances_to_bulk_create.append(object)
            if object.image:
                images_to_delete.append(object.image.name)

        # django의 bulk_create를 통해 전달된 model의 instance들을 한꺼번에 생성
        model.objects.bulk_create(instances_to_bulk_create)

        # 생성된 이미지 파일들을 삭제
        cls._delete_temporary_images(images_to_delete)

    @classmethod
    def _instantiate_model(cls, insert_value, model, **kwargs):
        """
        model 을 text 혹은 image로 나누어 instance를 만듬

        :param insert: Delta Operation 의 insert key에 대한 value.
                    text 혹은 {"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}
        :param model: Quill JS의 한 Operation이 저장될 Django의 모델
        :param **kwargs:
                - attributes: (None or attribute from insert),
                - post: 위 모델에 연결될 Foreignkey 모델 Instance
                - line_no: 해당 delta operation이 있었던 줄 번호
        :return: model 에 대한 객체
        """
        object = model(**kwargs)  # creates class instance with attribute and answer first
        try:  # extract image from insert if exists
            image_data_string = insert_value['image']
            if image_data_string[:4] == "data":  # check if the value is not already a url
                image_type, decoded_data = cls._split_image_base64(
                    image_data_string=image_data_string
                )
                filename = cls._save_image(
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

    @classmethod
    def _split_image_base64(cls, image_data_string):
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

    @classmethod
    def _save_image(cls, image_type, decoded_data, answer, **kwargs) -> string:
        """
        Saves os
        :param image_type:
        :param decoded_data:
        :param post:
        :param classname:
        :return:
        """
        # Create filename
        rand_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        filename = f'a-{answer.pk}__{rand_str}.{image_type}'
        cls._save_temporary_image(filename, decoded_data)
        return filename

    @classmethod
    def _save_temporary_image(cls, filename, decoded_data):
        """
        추후 Async로 변경

        :param filename:
        :param decoded_data:
        :return:
        """
        with open(filename, 'wb') as f:
            f.write(decoded_data)
            f.close()

    @classmethod
    def _delete_temporary_images(cls, *args, **kwargs):
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

    @classmethod
    def update_delta_operation_list(cls, queryset, content, model, **kwargs):

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
            in enumerate(cls.get_delta_operation_list(content, iterator=True), start=1)
        }

        instance_delta_set = set(instance_delta_instance_dict.keys())
        request_delta_set = set(request_delta_line_no_dict.keys())

        to_update = instance_delta_set & request_delta_set
        to_create = request_delta_set - instance_delta_set
        to_delete = instance_delta_set - request_delta_set

        # update
        # # replace instance line_no with request line_no
        for delta_operation in to_update:
            new_line_no = request_delta_line_no_dict[delta_operation]
            instance = instance_delta_instance_dict[delta_operation]
            instance.line_no = new_line_no
            instance.save()

        # create
        # create instance with request line_no
        for delta_operation in to_create:
            line_no = request_delta_line_no_dict[delta_operation]
            delta_operation = delta_operation.replace("'", '"')
            delta_content = json.loads(json.loads((json.dumps(delta_operation))))
            cls.save_delta_operation(delta_content=delta_content,
                                     model=model,
                                     line_no=line_no,
                                     **kwargs)
        # delete
        # delete instance with delta op value
        for delta_operation in to_delete:
            instance = instance_delta_instance_dict[delta_operation]
            instance.delete()

    @classmethod
    def save_delta_operation(cls, delta_content, model, **kwargs):
        """
        전달받은 model변수에 해당하는 Django 모델명에 대해 create를 통해 content를 저장

        :param delta_content: delta content 한 줄
        :param model: Quill JS의 한 Operation이 저장될 Django의 모델
        :param **kwargs:
                - answer: 위 모델에 연결될 Foreignkey 모델 Instance

        :return: 반환값은 없으며 create와 image create를 실행
        """
        insert_value, attributes = delta_content['insert'], \
                                   delta_content.get('attributes', None)

        object = cls._instantiate_model(
            insert_value=insert_value,
            model=model,
            attributes_value=attributes,
            **kwargs
        )
        if object.image:
            cls._delete_temporary_images(object.image.name)

        object.save()

    @classmethod
    @atomic
    def bulk_save_instance(cls):
        """
        Utilizes Django transaction.atomic to generate a single query for save on multiple instances
        :return:
        """

        pass

    @classmethod
    @atomic
    def bulk_delete_instance(cls):
        """

        :return:
        """
        pass

    @classmethod
    def _change_line_no(cls):
        pass

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

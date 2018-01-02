import base64
import json
import random
import re
import string
from collections import OrderedDict, defaultdict
from io import BytesIO

from PIL import Image as pil
from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models.query import QuerySet
from w3lib.url import url_query_cleaner

__all__ = (
    'DjangoQuill',
)


class DjangoQuill:
    """
    QuillJSDelta가 저장되는 model과 ForeignKey로 연결되어있는 parent_model을 Parsing 해주는 Class
    custom field -
    """

    def __init__(self, model=None, parent_model=None):
        self.model = model
        self.parent_model = parent_model
        self.parent_instance = None

    #     self._validate()
    #
    # def _validate(self):
    #     self._validate_django_model()
    #     self._validate_model_fields()
    #     self._validate_line_no_in_model()
    #
    # def _validate_django_model(self):
    #     """
    #     model과 parent_model이 Django 모델인지 확인
    #     :return:
    #     """
    #     assert type(self.model) == ModelBase, "Initialized model is not an instance of Django's ModelBase."
    #     assert type(
    #         self.parent_model) == ModelBase, "Initialized parent model is not an instance of Django's ModelBase."
    #
    # def _validate_model_fields(self):
    #     """
    #     model이 parent_model에 ForeignKey 관계를 갖는지 확인
    #     :return:
    #     """
    #     foreignkey_field = self._get_related_field()
    #     if not foreignkey_field:
    #         raise AttributeError("self.model and self.parent_model are not related.")
    #
    # def _validate_line_no_in_model(self):
    #     """
    #     model에 line_no 라는 이름의 필드가 존재하는지 확인하며 Integer필드인지 확인
    #     :return:
    #     """
    #     field_names = [field.name for field in self.model._meta.fields]
    #     if "line_no" not in field_names:
    #         raise AttributeError("line_no not in self.model")

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

    def get_delta_operation_instances(self, content, parent_instance):
        """
        self.model에 대해 bulk_create를 통해 content를 저장

        :param content: Content의 정보가 들은 delta안의 list
        :param instance: 위 모델에 연결될 Foreignkey 모델의 Instance, parent_model의 Instance

        :return: 반환값은 없으며 bulk_create와 이미지 삭제 함수를 실행
        """
        # Instance가 parent_model의 instance인지 확인
        self.parent_instance = parent_instance
        # Bulk Create할 instance를 모아둘 list instantiation
        # get_delta_operation_list() 를 통해 content에서 delta operation이 담긴 list 반환
        # 반환받은 list 내에 있는 quill_delta_operation에 대해 self.model을 instantiate
        delta_list = self.get_delta_operation_list(content, iterator=True)

        for line_no, quill_delta_operation in enumerate(delta_list, start=1):
            model_instance = self._instantiate_model(
                quill_delta_operation=quill_delta_operation,
                line_no=line_no,
                parent_instance=parent_instance
            )
            if type(model_instance) == Exception:
                raise model_instance
            yield model_instance

    def _instantiate_model(self, quill_delta_operation, line_no, parent_instance):
        """
        model 을 instantiate 할 때 필요한 정보를 kwargs로 만들어 전달

        :param quill_delta_operation:
        :param line_no:
        :param instance:
        :return:
        """
        insert_value = quill_delta_operation.get('insert')
        attributes = quill_delta_operation.get('attributes')
        video = quill_delta_operation.get('video')
        field_name = self._get_related_field()
        kwargs = {
            "insert_value": insert_value,
            "attributes_value": attributes,
            "video_insert_value": video,
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
        image_value = insert_value.get('image') if type(insert_value) == dict else None
        if image_value:
            try:
                decoded_data = self._parse_base64(image_base64=image_value)
                filename = self._generate_filename(**kwargs)
                image = self._image_process(data=decoded_data, max_size=600)
                instance.image.save(
                    filename,
                    image,
                    save=False,
                )
                url = url_query_cleaner(instance.image.url)
                instance.image_insert_value = {"image": f"{url}"}

            # image 가 base64가 아닌 경우
            # url 주소일 경유 담겨있을 경우 image_insert_value에 url 추가
            # image 가 base64도 아니고 link도 아닌 잘못된 형식일 경우 ValueError
            except AttributeError:
                if image_value[:4] == "http" or image_value[:6] == settings.MEDIA_URL:
                    instance.image_insert_value = {"image": f"{image_value}"}
                else:
                    raise ValueError("올바른 형태의 이미지 Base64가 아닙니다. data:image/png;base64로 시작하는지 확인해주세요 ")
        # insert 안에 Text만 있을 경우
        else:
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

    def _generate_filename(self, **kwargs) -> string:
        """
        이미지 파일 이름 생성

        :param format: 파일 형태 format
        :return:
        """
        fk_field_name = self._get_related_field()
        fk_field_instance = kwargs.get(fk_field_name)

        # Create filename
        rand_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        filename = f'{fk_field_instance.pk}/{rand_str}.jpeg'

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

        # 이미지의 가로 혹은 이미지의 세로가 max_size보다 클 경우
        # 긴 쪽을 max_size에 맞추고 짧은 쪽을 max_size * ratio 으로 이미지를 resize
        if gtr_side > max_size:
            if src_width > src_height:
                dst_width = max_size
                dst_height = int(src_height * ratio)
            else:
                dst_height = max_size
                dst_width = int(src_width * ratio)
            img = img.resize((dst_width, dst_height))

        output_img = BytesIO()
        img.save(output_img, 'JPEG')
        return output_img

    def img_base64_to_link(self, objs: QuerySet, html: str):
        """
        HTML String의 Base64 이미지들을 objs의 Queryset에 있는 이미지 url로 replace하여 새 HTML String을 반환
        :param objs:
        :param html:
        :return:
        """
        soup = BeautifulSoup(html, 'html.parser')
        img_tags = soup.find_all("img")
        for obj, img_tag in zip(objs, img_tags):
            # Get rid of Amazon Token
            url = url_query_cleaner(obj.image.url)
            new_img_tag = soup.new_tag('img', src=url)
            img_tag.replace_with(new_img_tag)
        return str(soup)

    def html_preview_parse(self, html: str, preview_len: int):
        soup = BeautifulSoup(html, 'html.parser')
        tgt_text = soup.get_text()[:preview_len]
        if len(tgt_text) < preview_len:
            return str(soup)

        char_len = 0
        for content in soup.contents[0]:
            content_text = content.get_text()
            if content_text not in tgt_text:
                length = preview_len - char_len
                content.string = content_text[:length] + "..."
                for i, content in enumerate(content.find_all_next()):
                    if i > 0:
                        content.decompose()
        return str(soup)

    def update_delta_operation_list(self, queryset: QuerySet,
                                    content: dict, parent_instance):
        """
        전달받은 model에 대해 update, delete create을 실행

        :param queryset: Quill Operation 이 담겨있는 Queryset
        :param content: request.data의 content
        :param parent_instance: Quill Operation 와 ForeignKey로 연결되는 parent_instance
        :return:
        """

        # Queryset 에서 {Quill operation : instance, ...} 형식의 dict 생성
        # Quill operation 은 json dumps를 통한 string 형태
        operation_instance_dict = defaultdict(list)
        for qdo_instance in queryset:
            operation_instance_dict[json.dumps(qdo_instance.delta_operation)].append(qdo_instance)

        # Request.data.content 에서 {Quill operation : line_number, ...} 형식의 dict 생성
        # Quill operation 은 json dumps를 통한 string 형태
        operation_lineno_dict = defaultdict(list)
        for line_no, qdo in enumerate(self.get_delta_operation_list(content, iterator=True), start=1):
            operation_lineno_dict[json.dumps(qdo)].append(line_no)

        # 델타 줄의 string들에 대해서 set operation을 실행,
        # to_update: 같은 내용의 경우, line number를 update 해야 되는 내용
        # to_create: 새로운 내용일 경우, 새 instance를 create 해야 되는 내용
        # to_delete: 지워야 하는 내용일 경우, 지워진 내용
        instance_delta_list = list()
        for item in operation_instance_dict.items():
            for i in range(len(item[1])):
                instance_delta_list.append(item[0])
        request_delta_list = list()
        for item in operation_lineno_dict.items():
            for i in range(len(item[1])):
                request_delta_list.append(item[0])
        set_i = set(instance_delta_list)
        set_r = set(request_delta_list)
        to_update = [item for item in instance_delta_list if item in set_i and item in set_r]
        to_create = [item for item in request_delta_list if item not in set_i]
        to_delete = [item for item in instance_delta_list if item not in set_r]
        to_update_list = self._get_instantces_to_update(
            to_update=to_update,
            operation_lineno_dict=operation_lineno_dict,
            operation_instance_dict=operation_instance_dict
        )
        to_create_list = self._get_instantces_to_create(
            to_create=to_create,
            operation_lineno_dict=operation_lineno_dict,
            parent_instance=parent_instance
        )
        to_delete_list = self._get_instantces_to_delete(
            to_delete=to_delete,
            operation_instance_dict=operation_instance_dict
        )
        return to_update_list, to_create_list, to_delete_list

    def _get_instantces_to_update(self, to_update: list, operation_lineno_dict: dict, operation_instance_dict: dict):
        """
        이미 존재하는 operation에 대해 line number을 업데이트

        :param to_update:
        :param operation_lineno_dict:
        :param operation_instance_dict:
        :return:
        """
        result = list()
        # update
        # replace instance line_no with request line_no
        for delta_operation in to_update:
            new_line_nos = operation_lineno_dict[delta_operation]
            dt_instances = operation_instance_dict[delta_operation]
            for instance, line_no in zip(dt_instances, new_line_nos):
                instance.line_no = line_no
                yield instance

    def _get_instantces_to_create(self, to_create: list, operation_lineno_dict: dict, parent_instance):
        """

        :param to_create:
        :param operation_lineno_dict:
        :param instance:
        :return:
        """
        # create
        # create instance with request line_no

        for delta_operation_str in to_create:
            # Get line_no
            # Get delta_operation
            # instantiate model for bulk create
            line_no = operation_lineno_dict[delta_operation_str].pop()
            quill_delta_operation = json.loads(json.loads((json.dumps(delta_operation_str))))
            instance = self._instantiate_model(
                quill_delta_operation=quill_delta_operation,
                line_no=line_no,
                parent_instance=parent_instance
            )
            yield instance

    def _get_instantces_to_delete(self, to_delete: list, operation_instance_dict: dict):
        """

        :param to_delete:
        :param operation_instance_dict:
        :return:
        """
        # delete
        # delete instance with delta op value
        for delta_operation in to_delete:
            instance = operation_instance_dict[delta_operation].pop()
            yield instance

import base64
import json
import random
import re
import string

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class QuillJSImageProcessor:
    def get_delta(self, content):
        """
        Request에서 content부분을 뽑아내 json을 만듬
        {'content':{"ops":[{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}]}}
        ->
        {"ops":[{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}]}
        :return:
        """
        return json.loads(content)

    def get_delta_list(self, delta):
        """
        {"ops":[{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}]}
        ->
        ([{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}])
        :param json_data: QuillJS의 json 형태의 data
        :return:
        """
        return delta['ops']

    def get_image_base64(self, item):
        """
        {"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}}
        ->
        "data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="
        :param item: json item
        :return:
        """
        try:
            return item['insert']['image']
        except:
            return None

    def split_image_base64(self, image_data_string):
        """

        :param image_data_string:
        :return:
        """
        data = re.match(r'\w+:image\/(\w+);\w+,(.+)', image_data_string)
        image_type = data.group(1)
        byte_data_string = data.group(2)
        byte_data_base64 = bytes(byte_data_string, 'utf-8')
        decoded_data = base64.b64decode(byte_data_base64)
        return image_type, decoded_data

    def save_image_file(self, image_type, decoded_data, question):
        """

        :param image_type:
        :param decoded_data:
        :param answer_pk:
        :return:
        """
        rand_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        filename = f'q-{question}__{rand_str}.{image_type}'
        file = default_storage.save(filename, ContentFile(decoded_data))
        url = default_storage.url(filename)

        return url  # boto3에 저장된 이미지의 url 반환

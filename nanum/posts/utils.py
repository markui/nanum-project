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

    def get_delta_list(self, delta, iterator=False):
        """
        {"ops":[{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}]}
        ->
        ([{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}])
        :param json_data: QuillJS의 json 형태의 data
        :return:
        """
        if iterator:
            return iter(delta['ops'])
        return delta['ops']

    def get_image_url(self, item, question):
        """
        {"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}}
        ->
        "data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="
        except not image, return None
        else already url, return url
        ->
        "<image_url>"
        :param item: json item
        :return: 저장된 이미지의 url
        """
        try:
            image_data_string = item['insert']['image']
            if image_data_string[:4] != "data": # 만약 image_data_string이 이미 url일 경우
                return image_data_string
        except TypeError:
            return None

        image_type, decoded_data = self.split_image_base64(image_data_string=image_data_string)
        url = self.save_image_file(image_type=image_type, decoded_data=decoded_data, question=question)
        return url

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

    def delete_image_file(self, *args):
        """
        Takes a single string of the name of the image or list of strings as args.
        If List, iterate through to delete the files in the list.
        If String, delete the single file.
        :param args:
        :return:
        """

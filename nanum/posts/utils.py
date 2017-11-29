import base64
import json
import os
import re

from posts.models.post import AnswerImage


class QuillJSImageProcessor:
    def quill_content_string_to_json(self, content):
        """
        Request에서 content부분을 뽑아내 json을 만듬
        {'content':{"ops":[{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}]}}
        ->
        {"ops":[{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}]}
        :return:
        """
        # try:
        #     content = request.data['content']
        # except KeyError:
        #     return ""
        return json.loads(content)

    def get_quill_content(self, json_data):
        """
        {"ops":[{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}]}
        ->
        iter([{"insert":{"image":"data:image/jpeg;base64,/9j/4AAQSkvI/cv2T+9n//2Q=="}},{"insert":"\n"}])
        :param json_data: QuillJS의 json 형태의 data
        :return:
        """
        return json_data['ops']

    def update_quill_content(self, json_data, new_content_data):
        """
        "ops"의 Value를 전달받은 new_content_Data로
        :param json_data:
        :param new_content_data:
        :return:
        """
        json_data['ops'] = new_content_data
        return json_data

    def get_quill_image_data_string(self, item):
        """

        :param item: json item
        :return:
        """
        try:
            return item['insert']['image']
        except:
            return None

    def image_data_string_split(self, image_data_string):
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

    def save_image_file(self, image_type, decoded_data, answer):
        """

        :param image_type:
        :param decoded_data:
        :param answer_pk:
        :return:
        """
        # set variables for filename
        answer_pk = answer.pk
        image_pk = answer.answer_image_set.count() + 1
        filename = f'a-{answer_pk}__i-{image_pk}.{image_type}'

        with open(filename, 'wb') as f:
            f.write(decoded_data)
            f.close()

        answer_image = self.save_answer_image_instance(image=filename, answer=answer)

        # 이미지가 저장된 후 이미지를 삭제
        os.remove(filename)
        return answer_image.image.url  # boto3에 저장된 이미지의 url 반환

    def save_answer_image_instance(self, image, answer):
        return AnswerImage.objects.create(image=image, answer=answer)

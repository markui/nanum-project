from rest_framework import status

from posts.apis import QuestionRetrieveUpdateDestroyView
from .base import QuestionBaseTest


class QuestionRetrieveUpdateDestroyViewTest(QuestionBaseTest):
    """
    RUD에 대한 요청 테스트
    url :       /post/question/{pk}
    method :    GET, DELETE, PUT, PATCH

    1. 만들어진 Question Object에 대해 retrieve가 잘 작동하는지 테스트(test_question_retrieve)
    2. 만들어진 Question Object에 대해 update(put)가 잘 작동하는지 테스트(test_question_put)
    3. 만들어진 Question Object에 대해 partial update(patch)가 잘 작동하는지 테스트(test_question_patch)
    4. 만들어진 Question Object에 대해 destroy(delete)가 잘 작동하는지 테스트(test_question_delete)
    """

    VIEW_CLASS = QuestionRetrieveUpdateDestroyView

    def test_question_retrieve(self):
        user = self.create_user(email='retrieve@siwon.com', password='dltldnjs')
        self.client.force_authenticate(user)
        temp_question = self.create_question(user=user)

        response = self.client.get(f'http://testserver/post/question/{temp_question.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_question_put(self):
        user = self.create_user(email='put@siwon.com', password='dltldnjs')
        self.client.force_authenticate(user)
        topic = self.create_topic(creator=user, name='put topic')
        question = self.create_question(user=user, content='put\'s content')
        # 질문 생성 후 토픽 추가
        question.topics.add(topic)
        # 업데이트 될 토픽
        topic_for_data = self.create_topic(creator=user, name='updated topic')

        data = {
            'content': 'updated content',
            'topics': topic_for_data.pk,
        }
        response = self.client.put(
            path=f'http://testserver/post/question/{question.pk}/',
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_question_patch(self):
        user = self.create_user(email='patch@siwon.com', password='dltldnjs')
        self.client.force_authenticate(user)
        topic = self.create_topic(creator=user, name='patch topic')
        question = self.create_question(user=user, content='patch\'s content')
        # 질문 생성 후 토픽 추가
        question.topics.add(topic)
        # 업데이트 될 토픽

        data = {
            'content': 'patch\'s updated content',
        }
        print(f'data : {data}')

        response = self.client.patch(
            path=f'http://testserver/post/question/{question.pk}/',
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_question_delete(self):
        user = self.create_user(email='delete@siwon.com', password='dltldnjs')
        self.client.force_authenticate(user)
        question = self.create_question(user=user, content='delete\'s content')
        response = self.client.delete(f'http://testserver/post/question/{question.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


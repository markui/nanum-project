from rest_framework import status

from ..base import QuestionBaseTest


class QuestionListCreateViewTest(QuestionBaseTest):
    """
    Question Objects 생성 테스트입니다.
    Question의 파라미터로 Topic 객체가 들어가므로 임의의 여러 Topic을 생성 후
    Question 객체의 생성을 테스트 합니다.
    url :       /post/question/
    method :    post
    """

    def test_create_question(self):
        print("\n**********Question Objects 생성 테스트 입니다.**********\n")

        # 토픽 리스트를 저장 할 리스트
        topic_list = list()
        # /post/question/
        url = self.URL_API_QUESTION_LIST_CREATE
        users_queryset = self.create_random_users()
        topics = self.create_random_topics(users_queryset)
        # 토픽의 pk를 하나씩 리스트에 저장
        for topic in topics:
            topic_list.append(topic.pk)

        data = {
            'content': 'create question test content',
            'topics': topic_list,
        }
        print(f'====Question 객체를 생성할 때 필요한 data(위에 생성된 토픽들로 생성)====\n{data}\n')

        response = self.client.post(url, data=data, format='json')
        print(f'====RESPONSE====\n{response}\n')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        if response.status_code == 201:
            print('test_create_question 테스트 성공!\n')

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient

from posts.models import Question, Answer, Comment, CommentPostIntermediate
from topics.models import Topic

User = get_user_model()


class CustomBaseTest(APITestCase):
    # URL
    URL_API_ANSWER_LIST_CREATE_NAME = 'post:answer:answer-list'
    URL_API_ANSWER_MAIN_FEED_LIST_NAME = 'post:answer:answer-main'
    URL_API_ANSWER_DETAIL_NAME = 'post:answer:answer-detail'
    URL_API_COMMENT_LIST_CREATE_NAME = 'post:comment:comment-list'
    URL_API_COMMENT_DETAIL_NAME = 'post:comment:comment-detail'
    URL_API_ANSWER_LIST_CREATE = '/post/answer/'
    URL_API_ANSWER_MAIN_FEED_LIST = '/post/answer/main_feed/'
    URL_API_ANSWER_DETAIL = '/post/answer/{pk}/'
    URL_API_COMMENT_LIST_CREATE = '/post/comment/'
    URL_API_COMMENT_DETAIL = '/post/comment/{pk}/'
    URL_FILTER_USER = 'user={pk}'
    URL_FILTER_TOPIC = 'topic={pk}'
    URL_FILTER_BOOKMARKED = 'bookmarked={pk}'
    URL_FILTER_ORDERING = 'ordering={field}'

    # DATA
    USER_EMAIL_LIST = [
        'abc1@abc.com',
        'abc2@abc.com',
        'abc3@abc.com',
        'abc4@abc.com'
    ]
    TOPIC_NAME_LIST = [
        '컴공',
        '음악',
        '술',
        '우주과학'
    ]
    QUESTION_CONTENT = '{topic} - {user}의 질문'
    ANSWER_DELTA = {"ops": [{"insert": "Test Text\n"}]}
    ANSWER_HTML = '<div class="ql-editor" data-gramm="false" contenteditable="true" data-placeholder="Compose an epic...">' \
                  '<p>Test Text</p>' \
                  '</div>' \
                  '<div class="ql-clipboard" contenteditable="true" tabindex="-1"></div>' \
                  '<div class="ql-tooltip ql-hidden">' \
                  '<a class="ql-preview" target="_blank" href="about:blank"></a>' \
                  '<input type="text" data-formula="e=mc^2" data-link="https://quilljs.com" data-video="Embed URL">' \
                  '<a class="ql-action"></a>' \
                  '<a class="ql-remove"></a>' \
                  '</div>'

    @classmethod
    def create_user(cls, name, email):
        return User.objects.create_user(name=name, email=email, password='password')

    @classmethod
    def create_topic(cls, user, name):
        return Topic.objects.create(creator=user, name=name)

    @classmethod
    def create_question(cls, user, topic):
        content = cls.QUESTION_CONTENT.format(topic=topic, user=user)
        q = Question.objects.create(user=user, content=content)
        q.topics.add(topic)
        return q

    @classmethod
    def create_answer(cls, user: User, question: Question, content=ANSWER_DELTA,
                      content_html=ANSWER_HTML, return_response=False):
        # Answer의 경우 QuillJS Data의 포맷을 받아 생성해야 하기 때문에 REST API를 통해서 생성
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {user.token}')
        data = {
            'user': user.pk,
            'question': question.pk,
            'content': content,
            'content_html': content_html,
            'published': True,
        }
        response = client.post(cls.URL_API_ANSWER_LIST_CREATE, data=data, format='json')
        if return_response:
            return response
        return Answer.objects.get(pk=response.data['pk'])

    @classmethod
    def create_comment(cls, user, content="코멘트입니다.", question=None, answer=None, parent=None):
        if question:
            cpi = CommentPostIntermediate.objects.get(question=question)
        else:
            cpi = CommentPostIntermediate.objects.get(answer=answer)

        return Comment.objects.create(user=user, content=content, comment_post_intermediate=cpi, parent=parent)

    @classmethod
    def setUpTestData(cls):

        # 유저 생성
        users = []
        for email in cls.USER_EMAIL_LIST:
            user = cls.create_user(name=email, email=email)
            users.append(user)

        # Topic 생성
        # 유저 1 - Topic 1, 유저 2 - Topic 2,... 유저 n - Topic n
        topics = []
        for i, topic_name in enumerate(cls.TOPIC_NAME_LIST):
            topic = cls.create_topic(user=users[i],
                                     name=topic_name)
            topics.append(topic)

        # Question 생성
        # T = Question with Topic
        # 유저 1 - T 1, T 2, T 3, T 4, 유저 2 - T 1, T 2, T 3, T 4,...
        # 총 len(user) * len(topic) 만큼의 질문 생성
        questions = []
        for user in users:
            for topic in topics:
                question = cls.create_question(user=user, topic=topic.pk)
                questions.append(question)

        # Answer 생성
        # T{pk}_U{pk} = Q with T pk, U pk
        # 유저 1 - T1_U1, T1_U2, T1_U3, T1_U4, T2_U1...유저 2 - T1_U1,...
        # 총 len(user) * len(question) 만큼의 답변 생성
        answers = []
        for user in users:
            for topic in topics:
                for question_user in users:
                    question = Question.objects.get(user=question_user, topics=topic)
                    answer = cls.create_answer(user=user, question=question)
                    answers.append(answer)

        # Comment 생성
        # 모든 Question에 대하여 Comment 생성
        for question in questions:
            comment = cls.create_comment(user=users[0], question=question)


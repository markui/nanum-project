import random
from random import randrange, randint

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from posts.models import Question
from topics.models import Topic

User = get_user_model()


class QuestionBaseTest(APITestCase):
    # QuestionListCreateView
    URL_API_QUESTION_LIST_CREATE_NAME = 'post:question:list'
    URL_API_QUESTION_LIST_CREATE = '/post/question/'
    # QuestionMainFeedListView
    URL_API_QUESTION_MAIN_FEED_LIST_NAME = 'post:question:main-feed'
    URL_API_QUESTION_MAIN_FEED_LIST = '/post/question/main_feed/'
    # QuestionFilterListView
    URL_API_QUESTION_FILTER_LIST_NAME = 'post:question:topics-filter'
    URL_API_QUESTION_FILTER_LIST = '/post/question/filter/'

    # 생성될 랜덤한 유저의 수
    num_of_users = randint(5, 10)
    # 선택된 랜덤한 유저의 pk
    random_user_pk = randint(1, num_of_users)
    # 선택된 유저가 생성할 질문의 수
    num_of_questions = randint(11, 20)
    # 생성될 랜덤한 토픽의 수
    num_of_topics = randrange(1, 10)

    # query parameters
    query_params = [
        'user',
        'answered_by',
        'bookmarked_by',
        'followed_by',
        'topic',
        'ordering',
        'page',
    ]

    # 유저 생성
    @staticmethod
    def create_user(email='siwon@siwon.com', password='dltldnjs', is_none=False):
        if is_none:
            # user단에서 none객체 생성을 막아놓아서 테스트 불가(기본값과 같은 값이 들어가도록 설정)
            # return User.objects.create_user()
            return User.objects.create_user(email=email, password=password)
        return User.objects.create_user(email=email, password=password)

    # 토픽 생성
    @staticmethod
    def create_topic(creator=None, name='temp_topic'):
        return Topic.objects.create(creator=creator, name=name)

    # 질문 생성
    @staticmethod
    def create_question(user=None, content='default : 임시 컨텐츠 입니다.'):
        return Question.objects.create(
            user=user,
            content=content,
        )

    # 랜덤한 다수의 유저 생성 테스트
    def create_random_users(self, is_none=False):
        """
        랜덤한 수의 유저를 생성한다.
        특정 유저를 지정하거나, 랜덤한 유저를 지정할 수 있다.
        params :
            self.num_of_users
        :return: User.objects.filter(pk__in=user_list)
        """
        user_list = list()
        # 랜덤한 수의 유저 생성(is_none : True 일 경우 None객체 생성)
        for i in range(self.num_of_users):
            if is_none:
                # user단에서 none객체 생성을 막아놓아서 테스트(생성) 불가
                self.create_user(is_none=True)
            else:
                created_user = self.create_user(email=f'user_{i+1}@user.com')
                user_list.append(created_user.pk)

        print(f'====생성된 유저의 pk 리스트====\n {user_list} \n')

        # 생성하기로 한 유저의 수와 만들어진 유저의 수 비교
        self.assertEqual(
            len(User.objects.filter(pk__in=user_list)),
            self.num_of_users)

        return User.objects.filter(pk__in=user_list)

    # 랜덤한 다수의 토픽 생성 테스트
    def create_random_topics(self, users_queryset):
        """
        1. 유저의 pk의 값으로 랜덤한 수의 토픽을 생성한다.
        2. 생성된 토픽들의 pk를 리스트에 저장해 Topic Objects를 리턴한다.
        params :
            self.num_of_topics
        :return: Topic.objects.filter(pk__in=topic_list)
        """

        # 리턴될 토픽 리스트
        topic_list = list()
        print('====위 유저 중 임의의 user(creator)로 생성된 토픽 출력====')
        for i in range(self.num_of_topics):
            random_user = random.choice(users_queryset)
            # 랜덤한 유저(creator)로 다수의 토픽 생성
            user = User.objects.get(pk=random_user.pk)
            self.client.force_authenticate(user=user)

            topic = self.create_topic(creator=user, name=f'토픽 {i+1}')
            # 토픽이 생성될 때 마다 토픽 리스트에 추가
            topic_list.append(topic.pk)

            print(f'creator : {user.pk} -> '
                  f'topic : {topic.pk}')
        print('\n')

        # 만들어진 토픽의 개수와 생성하기로 한 토픽의 개수 비교
        self.assertEqual(
            len(Topic.objects.filter(pk__in=topic_list)),
            self.num_of_topics
        )

        return Topic.objects.filter(pk__in=topic_list)

    # 랜덤한 다수의 질문 생성 테스트
    def create_random_questions(self, users_queryset, topics_queryset):
        """
        1. 질문에 추가 할 토픽들을 만든다.
        2. 만들어진 질문에 토픽의 개수만큼 topic을 추가한다.
        params :
            self.num_of_topics
        :return: Question.objects.all()
        """
        question_list = list()

        # 질문의 add될 토픽 개수
        num_of_topics = topics_queryset.count()
        # 선택된 랜덤한 user로 랜덤한 개수의 questions 생성
        for i in range(self.num_of_questions):
            random_user = random.choice(users_queryset)
            print(f'====user.pk={random_user.pk}로 생성된 질문에 추가된 토픽들===')

            # 질문 생성
            question = self.create_question(
                user=random_user,
                content=f'{i+1} 컨텐츠 입니다.',
            )
            question_list.append(question.pk)
            # 생성된 질문에 토픽 개수만큼 랜덤한 토픽을 추가
            for j in range(num_of_topics):
                # 랜덤한 토픽 선택
                topic = random.choice(topics_queryset)
                # 생성된 질문에 선택된 토픽 추가
                question.topics.add(topic)

                print(f'question : {question.pk} -> topic : {topic.pk}')
            print('\n')

        self.assertEqual(
            len(Question.objects.filter(pk__in=question_list)),
            self.num_of_questions)
        return Question.objects.filter(pk__in=question_list)

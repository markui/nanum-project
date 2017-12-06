from rest_framework import generics, status, permissions
from rest_framework.response import Response

from ..models import Comment, CommentPostIntermediate
from ..serializers import CommentSerializer

__all__ = (
    'CommentListCreateView',
)


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        """
        generics의 get_queryset 함수 override
        Comment 중 User가 단 comment queryset 역참조하여 반환
        :return:
        """
        user = self.request.user
        return user.comment_set.all()

    def list(self, request, *args, **kwargs):
        """
        ListModelMixin의 list 함수 override
        User가 단 Comment 반환
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        CreateModelMixin의 create 함수 override
        request.data의 question혹은 answer를 get_comment_post_intermediate를 통해 연결된 comment_post_intermediate과 연동

        :param data:
        :return:
        """
        # Immutable 한 Queryset을 mutable 하게 만들기 위해 Deepcopy
        data = request.data.copy()
        comment_post_intermediate = self.get_comment_post_intermediate(data)
        data['comment_post_intermediate'] = comment_post_intermediate.pk

        # 기존 get_serializer 함수에 request.data가 아닌 post_type이 추가된 data를 인자로 전달
        serializer = self.get_serializer(data=data)

        # 기존 create 함수
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_comment_post_intermediate(self, data):
        """
        Create helper method
        Data에 Question pk가 왔으면 해당 Question과 매핑되어있는 PostType pk를 반환
        Answer pk 가 왔으면 해당 Answer과 매핑되어있는 PostType pk를 반환
        :param post_type:
        :return:
        """
        keys = data.keys()
        # data에 question과 answer 둘 다 왔을 경우 KeyError
        if 'question' in keys and 'answer' in keys:
            raise KeyError('Both answer and question given')

        # data에 question과 answer 둘 다 없을 경우 KeyError
        if 'question' not in keys and 'answer' not in keys:
            raise KeyError("Neither question nor answer given. Check capitalization.")

        # question 혹은 answer pk 를 통해 연결돈 PostManager instance를 반환
        try:
            question_pk = data.pop('question')[0]
            comment_post_intermediate = CommentPostIntermediate.objects.get(question=question_pk)
        except KeyError:
            answer_pk = data.pop('answer')[0]
            comment_post_intermediate = CommentPostIntermediate.objects.get(answer=answer_pk)
        return comment_post_intermediate

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

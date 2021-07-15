from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from comments.models import Comment
from comments.serializers import CommentSerializer
from commons.permissions import IsOwnerOrReadOnly
from commons import selectors


class CommentViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Comment.objects.all().select_related('author')
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.filter(author=user)

        username = self.request.query_params.get('username')
        if username is not None:
            queryset = queryset.filter(author__username=username)

        model_name = self.request.query_params.get('model_name')
        if model_name is not None:
            queryset = queryset.filter(content_type__mdoel=model_name)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get'], detail=True)
    def likers(self, request, *args, **kwargs):
        comment = self.get_object()
        return selectors.comment_likers(self, comment, request)
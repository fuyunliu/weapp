from rest_framework import mixins, viewsets
from comments.models import Comment
from comments.serializers import CommentSerializer
from commons.permissions import IsOwnerOrReadOnly


class CommentViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Comment.objects.all()
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

        queryset = queryset.select_related('author')

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

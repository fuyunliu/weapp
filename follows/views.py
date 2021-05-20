from rest_framework import mixins, viewsets
from follows.models import Follow
from follows.serializers import FollowSerializer
from commons.permissions import IsOwnerOrReadOnly


class FollowViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Follow.objects.all().select_related('sender', 'content_type')
    serializer_class = FollowSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.filter(sender=user)

        username = self.request.query_params.get('username')
        if username is not None:
            queryset = queryset.filter(sender__username=username)

        model_name = self.request.query_params.get('model_name')
        if model_name is not None:
            queryset = queryset.filter(content_type__model=model_name)

        queryset = queryset.select_related('sender')

        return queryset

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

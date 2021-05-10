from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from likes.models import Like
from likes.serializers import LikeSerializer


class LikeViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

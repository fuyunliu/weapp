from rest_framework import mixins, viewsets
from wechat.models import Message
from wechat.serializers import MessageSerializer
from commons.permissions import IsOwnerOrReadOnly


class MessageViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Message.objects.all().select_related('sender', 'receiver')
    serializer_class = MessageSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.filter(sender=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

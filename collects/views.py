from rest_framework import mixins, viewsets
from rest_framework.response import Response

from collects.models import Collect, Collection
from collects.serializers import CollectionSerializer, CollectSerializer
from commons.permissions import IsOwnerOrReadOnly


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.filter(user=user)

        queryset = queryset.select_related('user')

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CollectViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Collect.objects.all()
    serializer_class = CollectSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.filter(collection__user=user)

        username = self.request.query_params.get('username')
        if username is not None:
            queryset = queryset.filter(collection__user__username=username)

        model_name = self.request.query_params.get('model_name')
        if model_name is not None:
            queryset = queryset.filter(content_type__mdoel=model_name)

        queryset = queryset.select_related('collection__user')
        return queryset

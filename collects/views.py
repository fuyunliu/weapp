from rest_framework import mixins, viewsets
from rest_framework.decorators import action

from collects.models import Collect, Collection
from collects.serializers import CollectionSerializer, CollectSerializer
from commons.permissions import IsOwnerOrReadOnly
from commons import selectors


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all().select_related('owner')
    serializer_class = CollectionSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.filter(owner=user)

        queryset = queryset.select_related('owner')

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(methods=['get'], detail=True)
    def articles(self, request, *args, **kwargs):
        collection = self.get_object()
        return selectors.collection_articles(self, collection, request)

    @action(methods=['get'], detail=True)
    def pins(self, request, *args, **kwargs):
        collection = self.get_object()
        return selectors.collection_pins(self, collection, request)

    @action(methods=['get'], detail=True)
    def likers(self, request, *args, **kwargs):
        collection = self.get_object()
        return selectors.collection_likers(self, collection, request)

    @action(methods=['get'], detail=True)
    def followers(self, request, *args, **kwargs):
        collection = self.get_object()
        return selectors.collection_followers(self, collection, request)


class CollectViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Collect.objects.all().select_related('collection__owner')
    serializer_class = CollectSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.filter(collection__owner=user)

        username = self.request.query_params.get('username')
        if username is not None:
            queryset = queryset.filter(collection__owner__username=username)

        model_name = self.request.query_params.get('model_name')
        if model_name is not None:
            queryset = queryset.filter(content_type__mdoel=model_name)

        return queryset

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from commons.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from taggit.models import Tag, TaggedItem
from taggit.serializers import TagSerializer, TaggedItemSerializer, BulkTaggedSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(methods=['get'], detail=True)
    def items(self, *args, **kwargs):
        items = self.get_object().items.all()
        return Response(TaggedItemSerializer(items, many=True).data)


class TaggedItemViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = TaggedItem.objects.all().select_related('tag')
    serializer_class = TaggedItemSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'bulk':
            return BulkTaggedSerializer
        return self.serializer_class

    @action(methods=['post'], detail=False)
    def bulk(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        items = serializer.bulk_create()
        return Response(TaggedItemSerializer(items, many=True).data, status=status.HTTP_201_CREATED)

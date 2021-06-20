from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from taggit.models import Tag, TaggedItem
from taggit.serializers import TagSerializer, TaggedItemSerializer
from commons.permissions import IsOwnerOrReadOnly


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # 谁都可以删除吗？
    permission_classes = [IsAuthenticated]

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

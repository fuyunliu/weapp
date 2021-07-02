from django.db.models.expressions import Col
from rest_framework import viewsets, renderers
from rest_framework.decorators import action
from rest_framework.response import Response

from commons.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from commons.managers import GenericJoin
from likes.models import Like
from weblog.models import Article, Pin, Category, Topic, Tag
from weblog.serializers import ArticleSerializer, PinSerializer, CategorySerializer, TopicSerializer, TagSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.filter(status=Article.Status.PUBLISHED)\
        .annotate(like_id=Col(Like._meta.db_table, Like._meta.pk))\
        .select_related('author', 'category').prefetch_related('tags', 'topics')
    serializer_class = ArticleSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        join = GenericJoin(Article, Like, extra_fields=[('sender', user.pk)])
        queryset.query.join(join)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get'], detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        article = self.get_object()
        return Response(article.body_html)

    @action(methods=['get'], detail=True)
    def likers(self, request, *args, **kwargs):
        from oauth.serializers import UserSerializer
        article = self.get_object()
        queryset = article.likers.all()
        params = {'context': {'request': self.request}, 'many': True}
        return Response(UserSerializer(queryset, **params).data)

    @action(methods=['get'], detail=True)
    def collections(self, request, *args, **kwargs):
        from collects.serializers import CollectionSerializer
        article = self.get_object()
        queryset = article.collections.all()
        params = {'context': {'request': self.request}, 'many': True}
        return Response(CollectionSerializer(queryset, **params).data)


class PinViewSet(viewsets.ModelViewSet):
    queryset = Pin.objects.filter(pk__gt=0)\
        .annotate(like_id=Col(Like._meta.db_table, Like._meta.pk))\
        .select_related('author')
    serializer_class = PinSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        join = GenericJoin(Pin, Like, extra_fields=[('sender', user.pk)])
        queryset.query.join(join)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get'], detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        pin = self.get_object()
        return Response(pin.body_html)

    @action(methods=['get'], detail=True)
    def likers(self, request, *args, **kwargs):
        from oauth.serializers import UserSerializer
        pin = self.get_object()
        queryset = pin.likers.all()
        params = {'context': {'request': self.request}, 'many': True}
        return Response(UserSerializer(queryset, **params).data)

    @action(methods=['get'], detail=True)
    def collections(self, request, *args, **kwargs):
        from collects.serializers import CollectionSerializer
        pin = self.get_object()
        queryset = pin.collections.all()
        params = {'context': {'request': self.request}, 'many': True}
        return Response(CollectionSerializer(queryset, **params).data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(methods=['get'], detail=True)
    def followers(self, request, *args, **kwargs):
        from oauth.serializers import UserSerializer
        category = self.get_object()
        queryset = category.followers.all()
        params = {'context': {'request': self.request}, 'many': True}
        return Response(UserSerializer(queryset, **params).data)


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(methods=['get'], detail=True)
    def followers(self, request, *args, **kwargs):
        from oauth.serializers import UserSerializer
        topic = self.get_object()
        queryset = topic.followers.all()
        params = {'context': {'request': self.request}, 'many': True}
        return Response(UserSerializer(queryset, **params).data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]

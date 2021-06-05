from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, renderers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from commons.permissions import IsOwnerOrReadOnly
from likes.models import Like
from weblog.models import Article, Pin, Category, Topic, Tag
from weblog.serializers import ArticleSerializer, PinSerializer, CategorySerializer, TopicSerializer, TagSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().select_related('author', 'category').prefetch_related('tags', 'topics')
    serializer_class = ArticleSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ct = ContentType.objects.get_for_model(Article)
        qs = Like.objects.get_user_likes(self.request.user, ct)
        ctx['article_content_type'] = ct
        ctx['user_like_articles'] = set(qs.values_list('object_id', flat=True))
        return ctx

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
    queryset = Pin.objects.all().select_related('author')
    serializer_class = PinSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ct = ContentType.objects.get_for_model(Pin)
        qs = Like.objects.get_user_likes(self.request.user, ct)
        ctx['pin_content_type'] = ct
        ctx['user_like_pins'] = set(qs.values_list('object_id', flat=True))
        return ctx

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

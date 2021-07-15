from rest_framework import viewsets, renderers
from rest_framework.decorators import action
from rest_framework.response import Response

from commons import selectors
from commons.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from weblog.models import Article, Pin, Category, Topic
from weblog.serializers import ArticleSerializer, PinSerializer, CategorySerializer, TopicSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list' or self.action == 'retrieve':
            queryset = selectors.select_article(queryset, self.request)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        article.viewed()
        serializer = self.get_serializer(article)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        article = self.get_object()
        return Response(article.body_html)

    @action(methods=['get'], detail=True)
    def likers(self, request, *args, **kwargs):
        article = self.get_object()
        return selectors.article_likers(self, article, request)

    @action(methods=['get'], detail=True)
    def collections(self, request, *args, **kwargs):
        article = self.get_object()
        return selectors.article_collections(self, article, request)

    @action(methods=['get'], detail=True)
    def tags(self, request, *args, **kwargs):
        article = self.get_object()
        return selectors.article_tags(self, article, request)

    @action(methods=['get'], detail=True)
    def topics(self, request, *args, **kwargs):
        article = self.get_object()
        return selectors.article_topics(self, article, request)

    @action(methods=['get'], detail=True)
    def comments(self, request, *args, **kwargs):
        article = self.get_object()
        return selectors.article_comments(self, article, request)


class PinViewSet(viewsets.ModelViewSet):
    queryset = Pin.objects.all()
    serializer_class = PinSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list' or self.action == 'retrieve':
            queryset = selectors.select_pin(queryset, self.request)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get'], detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        pin = self.get_object()
        return Response(pin.body_html)

    @action(methods=['get'], detail=True)
    def likers(self, request, *args, **kwargs):
        pin = self.get_object()
        return selectors.pin_likers(self, pin, request)

    @action(methods=['get'], detail=True)
    def collections(self, request, *args, **kwargs):
        pin = self.get_object()
        return selectors.pin_collections(self, pin, request)

    @action(methods=['get'], detail=True)
    def comments(self, request, *args, **kwargs):
        pin = self.get_object()
        return selectors.pin_comments(self, pin, request)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(methods=['get'], detail=True)
    def followers(self, request, *args, **kwargs):
        category = self.get_object()
        return selectors.category_followers(self, category, request)


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(methods=['get'], detail=True)
    def followers(self, request, *args, **kwargs):
        topic = self.get_object()
        return selectors.topic_followers(self, topic, request)

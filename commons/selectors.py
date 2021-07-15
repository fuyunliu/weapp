from functools import partial

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.expressions import Col, Value
from django.db.models.fields import BooleanField
from django.db.models.sql.constants import LOUTER

from collects.serializers import CollectionSerializer
from comments.serializers import CommentSerializer
from commons.decorators import paginate
from commons.managers import GenericJoin
from follows.models import Follow
from likes.models import Like
from oauth.serializers import UserSerializer
from polls.serializers import QuestionSerializer
from taggit.serializers import TagSerializer
from weblog.models import Article, Pin
from weblog.serializers import ArticleSerializer, PinSerializer, CategorySerializer, TopicSerializer

UserModel = get_user_model()


def select_article(queryset, request):
    queryset = queryset.filter(status=Article.Status.PUBLISHED)
    ct = ContentType.objects.get_for_model(Article)

    # 是否被我喜欢
    join_cols = (('id', 'object_id'),)
    extra_conds = (('content_type', ct.pk), ('sender', request.user.pk))
    join = GenericJoin(Article, Like, LOUTER, join_cols, extra_conds=extra_conds)
    alias = queryset.query.join(join)

    # 增加判断喜欢字段
    queryset = queryset.annotate(like_id=Col(alias, Like._meta.pk)) \
        .select_related('author', 'category').prefetch_related('topics')

    return queryset


def select_pin(queryset, request):
    queryset = queryset.filter(pk__isnull=False)
    ct = ContentType.objects.get_for_model(Pin)

    # 是否被我喜欢
    join_cols = (('id', 'object_id'),)
    extra_conds = (('content_type', ct.pk), ('sender', request.user.pk))
    join = GenericJoin(Pin, Like, LOUTER, join_cols, extra_conds=extra_conds)
    alias = queryset.query.join(join)

    # 增加判断喜欢字段
    queryset = queryset.annotate(like_id=Col(alias, Like._meta.pk)) \
        .select_related('author')

    return queryset


def select_user(queryset, request):
    queryset = queryset.filter(is_active=True)
    ct = ContentType.objects.get_for_model(UserModel)

    # 是否被我关注
    join_cols = (('id', 'object_id'),)
    extra_conds = (('content_type', ct.pk), ('sender', request.user.pk))
    following_join = GenericJoin(UserModel, Follow, LOUTER, join_cols, extra_conds=extra_conds)
    following_alias = queryset.query.join(following_join)

    # 是否关注了我
    join_cols = (('id', 'sender_id'),)
    extra_conds = (('content_type', ct.pk), ('object_id', request.user.pk))
    followed_join = GenericJoin(UserModel, Follow, LOUTER, join_cols, extra_conds=extra_conds)
    followed_alias = queryset.query.join(followed_join)

    # 增加判断关注字段
    queryset = queryset.annotate(
        following_id=Col(following_alias, Follow._meta.pk),
        followed_id=Col(followed_alias, Follow._meta.pk)
    )

    return queryset


@paginate(serializer_class=partial(UserSerializer, expand=['is_following', 'is_followed']))
def user_following(view, instance, request):
    queryset = instance.following.all()
    queryset = select_user(queryset, request)
    return queryset


@paginate(serializer_class=partial(UserSerializer, expand=['is_following', 'is_followed']))
def user_followers(view, instance, request):
    queryset = instance.followers.all()
    queryset = select_user(queryset, request)
    return queryset


@paginate(serializer_class=ArticleSerializer)
def user_articles(view, instance, request):
    queryset = instance.articles.all()
    queryset = select_article(queryset, request)
    return queryset


@paginate(serializer_class=PinSerializer)
def user_pins(view, instance, request):
    queryset = instance.pins.all()
    queryset = select_pin(queryset, request)
    return queryset


@paginate(serializer_class=TagSerializer)
def user_tags(view, instance, request):
    queryset = instance.tags.all()
    return queryset


@paginate(serializer_class=QuestionSerializer)
def user_questions(view, instance, request):
    queryset = instance.questions.all()
    return queryset


@paginate(serializer_class=CommentSerializer)
def user_comments(view, instance, request):
    queryset = instance.comments.all()
    return queryset


@paginate(serializer_class=CollectionSerializer)
def user_collections(view, instance, request):
    queryset = instance.collections.all()
    return queryset


@paginate(serializer_class=CollectionSerializer)
def user_liking_collections(view, instance, request):
    queryset = instance.liking_collections.all()
    return queryset


@paginate(serializer_class=CollectionSerializer)
def user_following_collections(view, instance, request):
    queryset = instance.following_collections.all()
    return queryset


@paginate(serializer_class=CommentSerializer)
def user_liking_comments(view, instance, request):
    queryset = instance.liking_comments.all()
    return queryset


@paginate(serializer_class=ArticleSerializer)
def user_liking_articles(view, instance, request):
    queryset = instance.liking_articles.annotate(is_liked=Value(True, BooleanField()))
    return queryset


@paginate(serializer_class=PinSerializer)
def user_liking_pins(view, instance, request):
    queryset = instance.liking_pins.annotate(is_liked=Value(True, BooleanField()))
    return queryset


@paginate(serializer_class=CategorySerializer)
def user_following_categories(view, instance, request):
    queryset = instance.following_categories.all()
    return queryset


@paginate(serializer_class=TopicSerializer)
def user_following_topics(view, instance, request):
    queryset = instance.following_topics.all()
    return queryset


@paginate(serializer_class=UserSerializer)
def article_likers(view, instance, request):
    queryset = instance.likers.all()
    return queryset


@paginate(serializer_class=CollectionSerializer)
def article_collections(view, instance, request):
    queryset = instance.collections.all()
    return queryset


@paginate(serializer_class=TagSerializer)
def article_tags(view, instance, request):
    queryset = instance.tags.all()
    return queryset


@paginate(serializer_class=TopicSerializer)
def article_topics(view, instance, request):
    queryset = instance.topics.all()
    return queryset


@paginate(serializer_class=CommentSerializer)
def article_comments(view, instance, request):
    queryset = instance.comments.all()
    return queryset


@paginate(serializer_class=UserSerializer)
def pin_likers(view, instance, request):
    queryset = instance.likers.all()
    return queryset


@paginate(serializer_class=CollectionSerializer)
def pin_collections(view, instance, request):
    queryset = instance.collections.all()
    return queryset


@paginate(serializer_class=CommentSerializer)
def pin_comments(view, instance, request):
    queryset = instance.comments.all()
    return queryset


@paginate(serializer_class=ArticleSerializer)
def collection_articles(view, instance, request):
    queryset = instance.articles.all()
    return queryset


@paginate(serializer_class=PinSerializer)
def collection_pins(view, instance, request):
    queryset = instance.pins.all()
    return queryset


@paginate(serializer_class=UserSerializer)
def collection_likers(view, instance, request):
    queryset = instance.likers.all()
    return queryset


@paginate(serializer_class=UserSerializer)
def collection_followers(view, instance, request):
    queryset = instance.followers.all()
    return queryset


@paginate(serializer_class=UserSerializer)
def comment_likers(view, instance, request):
    queryset = instance.likers.all()
    return queryset


@paginate(serializer_class=UserSerializer)
def category_followers(view, instance, request):
    queryset = instance.followers.all()
    return queryset


@paginate(serializer_class=UserSerializer)
def topic_followers(view, instance, request):
    queryset = instance.followers.all()
    return queryset

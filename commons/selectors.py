from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.expressions import Col, Value
from django.db.models.fields import BooleanField
from django.db.models.sql.constants import LOUTER

from collects.serializers import CollectionSerializer
from comments.serializers import CommentSerializer
from commons.managers import GenericJoin
from commons.decorators import paginate
from follows.models import Follow
from likes.models import Like
from oauth.serializers import UserSerializer
from polls.serializers import QuestionSerializer
from taggit.serializers import TagSerializer
from weblog.models import Article, Pin
from weblog.serializers import ArticleSerializer, PinSerializer, CategorySerializer, TopicSerializer

UserModel = get_user_model()


def select_article(queryset, request):
    queryset = queryset.filter(status=Article.Status.PUBLISHED) \
        .annotate(like_id=Col(Like._meta.db_table, Like._meta.pk)) \
        .select_related('author', 'category').prefetch_related('tags', 'topics')

    ct = ContentType.objects.get_for_model(Article)
    join_cols = (('id', 'object_id'),)
    extra_conds = (('content_type', ct.pk), ('sender', request.user.pk))
    join = GenericJoin(Article, Like, LOUTER, join_cols, extra_conds=extra_conds)
    queryset.query.join(join)

    return queryset


def select_pin(queryset, request):
    queryset = queryset.filter(pk__isnull=False) \
        .annotate(like_id=Col(Like._meta.db_table, Like._meta.pk)) \
        .select_related('author')

    ct = ContentType.objects.get_for_model(Pin)
    join_cols = (('id', 'object_id'),)
    extra_conds = (('content_type', ct.pk), ('sender', request.user.pk))
    join = GenericJoin(Pin, Like, LOUTER, join_cols, extra_conds=extra_conds)
    queryset.query.join(join)

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


@paginate(serializer_class=ArticleSerializer)
def user_articles(view, user, request):
    queryset = user.articles.all()
    queryset = select_article(queryset, request)
    return queryset


@paginate(serializer_class=PinSerializer)
def user_pins(view, user, request):
    queryset = user.pins.all()
    queryset = select_pin(queryset, request)
    return queryset


@paginate(serializer_class=TagSerializer)
def user_tags(view, user, request):
    queryset = user.tags.all()
    return queryset


@paginate(serializer_class=QuestionSerializer)
def user_questions(view, user, request):
    queryset = user.questions.all()
    return queryset


@paginate(serializer_class=CommentSerializer)
def user_comments(view, user, request):
    queryset = user.comments.all()
    return queryset


@paginate(serializer_class=CollectionSerializer)
def user_collections(view, user, request):
    queryset = user.collections.all()
    return queryset


@paginate(serializer_class=CollectionSerializer)
def user_liking_collections(view, user, request):
    queryset = user.liking_collections.all()
    return queryset


@paginate(serializer_class=CollectionSerializer)
def user_following_collections(view, user, request):
    queryset = user.following_collections.all()
    return queryset


@paginate(serializer_class=CommentSerializer)
def user_liking_comments(view, user, request):
    queryset = user.liking_comments.all()
    return queryset


@paginate(serializer_class=ArticleSerializer)
def user_liking_articles(view, user, request):
    queryset = user.liking_articles.annotate(is_liked=Value(True, BooleanField()))
    return queryset


@paginate(serializer_class=PinSerializer)
def user_liking_pins(view, user, request):
    queryset = user.liking_pins.annotate(is_liked=Value(True, BooleanField()))
    return queryset


@paginate(serializer_class=CategorySerializer)
def user_following_categories(view, user, request):
    queryset = user.following_categories.all()
    return queryset


@paginate(serializer_class=TopicSerializer)
def user_following_topics(view, user, request):
    queryset = user.following_topics.all()
    return queryset


@paginate(serializer_class=UserSerializer)
def user_following(view, user, request):
    queryset = user.following.all()
    return queryset


@paginate(serializer_class=UserSerializer)
def user_followers(view, user, request):
    queryset = user.followers.all()
    return queryset

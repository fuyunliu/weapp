from functools import partial

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Count
from django.db.models.expressions import Case, When, Value, Col
from django.db.models.fields import BooleanField
from django.db.models.sql.constants import LOUTER

from collects.serializers import CollectionSerializer
from comments.serializers import CommentSerializer
from commons.decorators import paginate, add_query
from commons.managers import GenericJoin
from follows.models import Follow
from likes.models import Like
from oauth.serializers import UserSerializer
from polls.serializers import QuestionSerializer
from taggit.serializers import TagSerializer
from weblog.models import Article, Post
from weblog.serializers import ArticleSerializer, PostSerializer, CategorySerializer, TopicSerializer

UserModel = get_user_model()


def is_expanded(request, field):
    expand_fields = request.query_params.get('expand', [])
    expand_fields = expand_fields and expand_fields.split(',')
    return field in expand_fields


def add_is_following(queryset, request):
    # 是否被当前用户关注
    ct = ContentType.objects.get_for_model(queryset.model)
    join_cols = (('id', 'object_id'),)
    extra_conds = (('content_type', ct.pk), ('sender', request.user.pk))
    join = GenericJoin(queryset.model, Follow, LOUTER, join_cols, extra_conds=extra_conds)
    alias = queryset.query.join(join)
    queryset = queryset.alias(following_id=Col(alias, Follow._meta.pk)) \
        .annotate(is_following=Case(
            When(following_id__isnull=True, then=Value(False)), default=Value(True), output_field=BooleanField())
    )
    return queryset


def add_is_followed(queryset, request):
    # 是否关注了当前用户
    ct = ContentType.objects.get_for_model(queryset.model)
    join_cols = (('id', 'sender_id'),)
    extra_conds = (('content_type', ct.pk), ('object_id', request.user.pk))
    join = GenericJoin(queryset.model, Follow, LOUTER, join_cols, extra_conds=extra_conds)
    alias = queryset.query.join(join)
    queryset = queryset.alias(followed_id=Col(alias, Follow._meta.pk)) \
        .annotate(is_followed=Case(
            When(followed_id__isnull=True, then=Value(False)),
            default=Value(True),
            output_field=BooleanField()
        ))
    return queryset


def add_is_liked(queryset, request):
    # 是否被当前用户喜欢
    ct = ContentType.objects.get_for_model(queryset.model)
    join_cols = (('id', 'object_id'),)
    extra_conds = (('content_type', ct.pk), ('sender', request.user.pk))
    join = GenericJoin(queryset.model, Like, LOUTER, join_cols, extra_conds=extra_conds)
    alias = queryset.query.join(join)
    queryset = queryset.alias(like_id=Col(alias, Like._meta.pk)) \
        .annotate(is_liked=Case(
            When(like_id__isnull=True, then=Value(False)),
            default=Value(True),
            output_field=BooleanField()
        ))
    return queryset


def select_article(queryset, request):
    queryset = queryset.filter(status=Article.Status.PUBLISHED)

    # 是否被当前用户喜欢
    queryset = add_is_liked(queryset, request)

    # 增加属性字段
    queryset = queryset.annotate(
        like_count=Count('likes'),
        comment_count=Count('comments'),
        collect_count=Count('collects')) \
        .select_related('author__profile', 'category') \
        .prefetch_related('topics')

    return queryset


def select_post(queryset, request):
    queryset = queryset.filter(pk__isnull=False)

    # 是否被当前用户喜欢
    queryset = add_is_liked(queryset, request)

    # 增加属性字段
    queryset = queryset.annotate(
        like_count=Count('likes'),
        comment_count=Count('comments'),
        collect_count=Count('collects')) \
        .select_related('author__profile')

    return queryset


def select_user(queryset, request):
    queryset = queryset.filter(is_active=True).select_related('profile')

    # 是否被当前用户关注
    if is_expanded(request, 'is_following'):
        queryset = add_is_following(queryset, request)

    # 是否关注了当前用户
    if is_expanded(request, 'is_followed'):
        queryset = add_is_followed(queryset, request)

    # 文章数量
    if is_expanded(request, 'article_count'):
        queryset = queryset.annotate(article_count=Count('articles'))

    # 动态数量
    if is_expanded(request, 'post_count'):
        queryset = queryset.annotate(post_count=Count('posts'))

    return queryset


@paginate(serializer_class=partial(UserSerializer, expand=['is_following', 'is_followed']))
@add_query(query_func=add_is_followed)
@add_query(query_func=add_is_following)
def user_following(view, instance, request):
    queryset = instance.following.all()
    queryset = select_user(queryset, request)
    return queryset


@paginate(serializer_class=partial(UserSerializer, expand=['is_following', 'is_followed']))
@add_query(query_func=add_is_followed)
@add_query(query_func=add_is_following)
def user_followers(view, instance, request):
    queryset = instance.followers.all()
    queryset = select_user(queryset, request)
    return queryset


@paginate(serializer_class=ArticleSerializer)
def user_articles(view, instance, request):
    queryset = instance.articles.all()
    queryset = select_article(queryset, request)
    return queryset


@paginate(serializer_class=PostSerializer)
def user_posts(view, instance, request):
    queryset = instance.posts.all()
    queryset = select_post(queryset, request)
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


@paginate(serializer_class=PostSerializer)
def user_liking_posts(view, instance, request):
    queryset = instance.liking_posts.annotate(is_liked=Value(True, BooleanField()))
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
def post_likers(view, instance, request):
    queryset = instance.likers.all()
    return queryset


@paginate(serializer_class=CollectionSerializer)
def post_collections(view, instance, request):
    queryset = instance.collections.all()
    return queryset


@paginate(serializer_class=CommentSerializer)
def post_comments(view, instance, request):
    queryset = instance.comments.all()
    return queryset


@paginate(serializer_class=ArticleSerializer)
def collection_articles(view, instance, request):
    queryset = instance.articles.all()
    return queryset


@paginate(serializer_class=PostSerializer)
def collection_posts(view, instance, request):
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

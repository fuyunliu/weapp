from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from weblog.models import Article, Pin, Category, Topic, Tag
from commons.fields.serializers import DynamicFieldsMixin


class ArticleSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    excerpt = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    # highlight = serializers.HyperlinkedIdentityField(view_name='article-highlight', format='html')
    is_liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    collect_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = '__all__'
        expandable_fields = ['body', 'body_html']

    def get_excerpt(self, obj):
        return obj.shorten(width=100)

    def get_content_type(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return f'{ct.app_label}.{ct.model}'

    def get_is_liked(self, obj):
        return (
            (hasattr(obj, 'like_id') and obj.like_id) or
            (hasattr(obj, 'is_liked') and obj.is_liked)
        )

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_collect_count(self, obj):
        return obj.collects.count()


class PinSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    excerpt = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    # highlight = serializers.HyperlinkedIdentityField(view_name='pin-highlight', format='html')
    is_liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    collect_count = serializers.SerializerMethodField()

    class Meta:
        model = Pin
        fields = '__all__'
        expandable_fields = ['body', 'body_html']

    def get_excerpt(self, obj):
        return obj.shorten(width=100)

    def get_content_type(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return f'{ct.app_label}.{ct.model}'

    def get_is_liked(self, obj):
        return (
            (hasattr(obj, 'like_id') and obj.like_id) or
            (hasattr(obj, 'is_liked') and obj.is_liked)
        )

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_collect_count(self, obj):
        return obj.collects.count()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Topic
        fields = '__all__'

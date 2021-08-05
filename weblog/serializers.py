from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from weblog.models import Article, Pin, Category, Topic
from commons.fields.serializers import TimesinceField


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.nickname')
    avatar = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    # highlight = serializers.HyperlinkedIdentityField(view_name='article-highlight', format='html')
    is_liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    collect_count = serializers.SerializerMethodField()
    created = TimesinceField()
    updated = TimesinceField()

    class Meta:
        model = Article
        fields = '__all__'

    def get_avatar(self, obj):
        return obj.author.gravatar()

    def get_excerpt(self, obj):
        return obj.shorten(width=200)

    def get_content_type(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return f'{ct.app_label}.{ct.model}'

    def get_is_liked(self, obj):
        return hasattr(obj, 'is_liked') and bool(obj.is_liked)

    def get_like_count(self, obj):
        return obj.like_count

    def get_comment_count(self, obj):
        return obj.comment_count

    def get_collect_count(self, obj):
        return obj.collect_count


class PinSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.nickname')
    avatar = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    # highlight = serializers.HyperlinkedIdentityField(view_name='pin-highlight', format='html')
    is_liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    collect_count = serializers.SerializerMethodField()
    created = TimesinceField()
    updated = TimesinceField()

    class Meta:
        model = Pin
        fields = '__all__'

    def get_avatar(self, obj):
        return obj.author.gravatar()

    def get_excerpt(self, obj):
        return obj.shorten(width=200)

    def get_content_type(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return f'{ct.app_label}.{ct.model}'

    def get_is_liked(self, obj):
        return hasattr(obj, 'is_liked') and bool(obj.is_liked)

    def get_like_count(self, obj):
        return obj.like_count

    def get_comment_count(self, obj):
        return obj.comment_count

    def get_collect_count(self, obj):
        return obj.collect_count


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.nickname')

    class Meta:
        model = Topic
        fields = '__all__'

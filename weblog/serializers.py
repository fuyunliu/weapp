from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from weblog.models import Article, Pin, Category, Topic, Tag


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    content_type = serializers.SerializerMethodField()
    highlight = serializers.HyperlinkedIdentityField(view_name='article-highlight', format='html')
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['body_html']

    def get_content_type(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return f'{ct.app_label}.{ct.model}'

    def get_is_liked(self, obj):
        return True if obj.like_id is not None else False


class PinSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    content_type = serializers.SerializerMethodField()
    highlight = serializers.HyperlinkedIdentityField(view_name='pin-highlight', format='html')
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Pin
        fields = '__all__'
        read_only_fields = ['body_html']

    def get_content_type(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return f'{ct.app_label}.{ct.model}'

    def get_is_liked(self, obj):
        return True if obj.like_id is not None else False


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Topic
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

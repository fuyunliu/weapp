from rest_framework import serializers
from weblog.models import Article, Pin, Category, Topic, Tag


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    content_type = serializers.SerializerMethodField()
    highlight = serializers.HyperlinkedIdentityField(view_name='article-highlight', format='html')
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['url', 'highlight', 'author', 'title', 'body', 'body_html', 'content_type', 'created', 'category', 'tags', 'topics', 'is_liked']
        read_only_fields = ['body_html']

    def get_content_type(self, obj):
        ct = self.context['article_content_type']
        return f'{ct.app_label}.{ct.model}'

    def get_is_liked(self, obj):
        return obj.pk in self.context['user_like_articles']


class PinSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    content_type = serializers.SerializerMethodField()
    highlight = serializers.HyperlinkedIdentityField(view_name='pin-highlight', format='html')
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Pin
        fields = ['url', 'highlight', 'author', 'body', 'body_html', 'content_type', 'created', 'is_liked']
        read_only_fields = ['body_html']

    def get_content_type(self, obj):
        ct = self.context['pin_content_type']
        return f'{ct.app_label}.{ct.model}'

    def get_is_liked(self, obj):
        return obj.pk in self.context['user_like_pins']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

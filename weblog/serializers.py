from rest_framework import serializers
from weblog.models import Article, Pin, Category, Topic, Tag


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='article-highlight', format='html')

    class Meta:
        model = Article
        fields = ['url', 'highlight', 'author', 'title', 'body', 'body_html', 'created', 'category', 'tags', 'topics']
        read_only_fields = ['body_html']


class PinSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='pin-highlight', format='html')

    class Meta:
        model = Pin
        fields = ['url', 'highlight', 'author', 'body', 'body_html', 'created']
        read_only_fields = ['body_html']


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

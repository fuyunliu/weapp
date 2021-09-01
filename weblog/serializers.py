from rest_framework import serializers

from commons.fields.serializers import UniqueFieldsMixin
from weblog.models import Article, Post, Category, Topic
from oauth.serializers import UserSerializer


class CategorySerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TopicSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Topic
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    excerpt = serializers.ReadOnlyField()
    content_type = serializers.ReadOnlyField()
    is_liked = serializers.ReadOnlyField()
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    collect_count = serializers.ReadOnlyField()
    category = CategorySerializer(label='分类', required=False, omit_fields=['name'])
    topics = TopicSerializer(label='话题', required=False, many=True, omit_fields=['name'])

    class Meta:
        model = Article
        fields = '__all__'

    def create(self, validated_data):
        topics = validated_data.pop('topics', [])
        article = Article.objects.create(**validated_data)
        for topic in topics:
            if topic.pk is None:
                topic.creator = article.author
                topic.save()
        article.topics.set(topics)

        return article

    def update(self, instance, validated_data):
        instance.title = validated_data['title']
        instance.body = validated_data['body']
        instance.category = validated_data['category']
        instance.save(update_fields=['title', 'body', 'category'])

        for topic in validated_data['topics']:
            if topic.pk is None:
                topic.creator = instance.author
                topic.save()
        instance.topics.set(validated_data['topics'])

        return instance

    def validate(self, attrs):
        # 处理文章分类
        category_data = attrs.pop('category', None)
        if category_data is not None:
            try:
                attrs['category'] = Category.objects.get(name=category_data['name'])
            except Category.DoesNotExist:
                attrs['category'] = Category.objects.get(pk=1)
        else:
            attrs['category'] = Category.objects.get(pk=1)

        # 处理文章话题
        topics_data = attrs.pop('topics', [])
        topics = attrs.setdefault('topics', [])
        for topic_data in topics_data:
            try:
                topic = Topic.objects.get(name=topic_data['name'])
            except Topic.DoesNotExist:
                topic = Topic(**topic_data)
            topics.append(topic)

        return attrs


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    excerpt = serializers.ReadOnlyField()
    content_type = serializers.ReadOnlyField()
    is_liked = serializers.ReadOnlyField()
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    collect_count = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = '__all__'

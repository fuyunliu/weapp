from rest_framework import serializers

from comments.models import Comment
from commons.fields.serializers import ContentTypeNaturalKeyField, GenericRelatedField, ContentTypeSerializer


class CommentSerializer(ContentTypeSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    content_type = ContentTypeNaturalKeyField(label='内容类型')
    content_object = GenericRelatedField(action_models='COMMENT_MODELS', read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['body_html', 'enabled']

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        return comment

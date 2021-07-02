from rest_framework import serializers

from comments.models import Comment
from commons.fields.serializers import ContentTypeNaturalKeyField, GenericRelatedField, ContentTypeMixin


class CommentSerializer(ContentTypeMixin, serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    content_type = ContentTypeNaturalKeyField(label='内容类型')
    content_object = GenericRelatedField(action_models='COMMENT_MODELS', read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['body_html', 'enabled']

    def create(self, validated_data):
        comment = Comment.objects.create(
            body=validated_data['body'],
            author=validated_data['author'],
            parent=validated_data.get('parent'),
            content_type=validated_data['content_type'],
            object_id=validated_data['instance'].pk
        )
        return comment

from rest_framework import serializers

from likes.models import Like
from commons.fields.serializers import ContentTypeNaturalKeyField, GenericRelatedField, ContentTypeMixin


class LikeSerializer(ContentTypeMixin, serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')
    content_type = ContentTypeNaturalKeyField(label='内容类型')
    content_object = GenericRelatedField(action_models='LIKE_MODELS', read_only=True)

    class Meta:
        model = Like
        fields = '__all__'

    def create(self, validated_data):
        like, _ = Like.objects.get_or_create(
            sender=validated_data['sender'],
            content_type=validated_data['content_type'],
            object_id=validated_data['instance'].pk
        )
        return like

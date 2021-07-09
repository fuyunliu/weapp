from rest_framework import serializers

from follows.models import Follow
from commons.fields.serializers import ContentTypeNaturalKeyField, GenericRelatedField, CheckContentTypeMixin


class FollowSerializer(CheckContentTypeMixin, serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')
    content_type = ContentTypeNaturalKeyField(label='内容类型')
    content_object = GenericRelatedField(action_models='FOLLOW_MODELS', read_only=True)

    class Meta:
        model = Follow
        fields = '__all__'

    def create(self, validated_data):
        follow, _ = Follow.objects.get_or_create(
            sender=validated_data['sender'],
            content_type=validated_data['content_type'],
            object_id=validated_data['instance'].pk
        )
        return follow

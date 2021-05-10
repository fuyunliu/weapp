from rest_framework import serializers
from likes.models import Like
from commons.fields.serializers import ContentTypeNaturalKeyField, LikedObjectRelatedField


class LikeSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')
    # content_type = serializers.ReadOnlyField(source='content_type.model')
    content_object = LikedObjectRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = '__all__'

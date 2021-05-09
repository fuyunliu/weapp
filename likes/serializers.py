from rest_framework import serializers
from likes.models import Like
from commons.fields.serializers import ContentTypeNaturalKeyField, LikedObjectRelatedField


class LikeSerializer(serializers.ModelSerializer):
    content_object = LikedObjectRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = '__all__'

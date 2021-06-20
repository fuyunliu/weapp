from rest_framework import serializers

from taggit.models import Tag, TaggedItem
from commons.fields.serializers import ContentTypeNaturalKeyField, GenericRelatedField, ContentTypeSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TaggedItemSerializer(ContentTypeSerializer):
    content_type = ContentTypeNaturalKeyField(label='内容类型')
    content_object = GenericRelatedField(action_models='TAGGIT_MODELS', read_only=True)

    class Meta:
        model = TaggedItem
        fields = '__all__'

    def create(self, validated_data):
        tagged_item, _ = TaggedItem.objects.get_or_create(**validated_data)
        return tagged_item

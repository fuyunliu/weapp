from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from collects.models import Collect, Collection
from commons.constants import Messages
from commons.fields.serializers import ContentTypeNaturalKeyField, GenericRelatedField, ContentTypeSerializer


class CollectionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Collection
        fields = '__all__'


class CollectSerializer(ContentTypeSerializer):
    content_type = ContentTypeNaturalKeyField(label='内容类型')
    content_object = GenericRelatedField(action_models='COLLECT_MODELS', read_only=True)

    class Meta:
        model = Collect
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)

        request = self.context['request']
        collection = attrs['collection']
        if collection.owner != request.user:
            raise ValidationError({'collection': Messages.COLLECTION_NOT_ALLOWED})

        return attrs

    def create(self, validated_data):
        collect, _ = Collect.objects.get_or_create(**validated_data)
        return collect

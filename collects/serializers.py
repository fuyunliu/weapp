from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from collects.models import Collect, Collection
from commons.constants import Messages
from commons.fields.serializers import ContentTypeNaturalKeyField, GenericRelatedField


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Collection
        fields = '__all__'


class CollectSerializer(serializers.HyperlinkedModelSerializer):
    content_type = ContentTypeNaturalKeyField(label='内容类型')
    content_object = GenericRelatedField(action_models='COLLECT_MODELS', read_only=True)

    class Meta:
        model = Collect
        fields = '__all__'

    def validate(self, attrs):
        content_type = attrs['content_type']
        action_models = getattr(self.fields['content_type'], 'action_models')

        model_path = f'{content_type.app_label}.{content_type.model}'
        if model_path not in getattr(settings, action_models, {}):
            raise ValidationError({'content_type': Messages.CONTENT_TYPE_NOT_ALLOWED})

        try:
            content_type.get_object_for_this_type(pk=attrs['object_id'])
        except ObjectDoesNotExist:
            raise ValidationError({'object_id': Messages.OBJECT_NOT_FOUND})

        request = self.context['request']
        collection = attrs['collection']
        if collection.owner != request.user:
            raise ValidationError({'collection': Messages.COLLECTION_NOT_ALLOWED})

        return attrs

    def create(self, validated_data):
        collect, _ = Collect.objects.get_or_create(**validated_data)
        return collect

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from follows.models import Follow
from commons.constants import Messages
from commons.fields.serializers import ContentTypeNaturalKeyField, GenericRelatedField


class FollowSerializer(serializers.HyperlinkedModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')
    content_type = ContentTypeNaturalKeyField(label='内容类型')
    content_object = GenericRelatedField(action_models='FOLLOW_MODELS', read_only=True)

    class Meta:
        model = Follow
        fields = '__all__'

    def validate(self, attrs):
        content_type = attrs['content_type']
        object_id = attrs['object_id']
        action_models = getattr(self.fields['content_object'], 'action_models')

        model_path = f'{content_type.app_label}.{content_type.model}'
        if model_path not in getattr(settings, action_models, {}):
            raise ValidationError({'content_type': Messages.CT_NOT_ALLOWED})

        try:
            content_type.get_object_for_this_type(pk=object_id)
        except ObjectDoesNotExist:
            raise ValidationError({'object_id': Messages.OBJECT_NOT_FOUND})

        return attrs

    def create(self, validated_data):
        follow, _ = Follow.objects.get_or_create(**validated_data)
        return follow

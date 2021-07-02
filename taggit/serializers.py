from operator import itemgetter
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.utils.serializer_helpers import ReturnList

from taggit.models import Tag, TaggedItem
from commons.constants import Messages
from commons.fields.serializers import ContentTypeNaturalKeyField, GenericRelatedField, ContentTypeMixin
from commons.utils import string_split


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TaggedItemSerializer(ContentTypeMixin, serializers.ModelSerializer):
    content_type = ContentTypeNaturalKeyField(label='内容类型')
    content_object = GenericRelatedField(action_models='TAGGIT_MODELS', read_only=True)

    class Meta:
        model = TaggedItem
        fields = '__all__'

    def validate(self, attrs):
        # 多重继承中的父类均有相同的子方法按照`__mro__`顺序查找并执行
        attrs = super().validate(attrs)

        instance = attrs['instance']
        request = self.context['request']
        if not (hasattr(instance, 'is_owned') and instance.is_owned(request.user)):
            raise ValidationError(Messages.INSTANCE_NOT_ALLOWED.format(attrs['content_type'], instance.pk))

        return attrs

    def create(self, validated_data):
        tagged_item, _ = TaggedItem.objects.get_or_create(
            tag=validated_data['tag'],
            content_type=validated_data['content_type'],
            object_id=validated_data['instance'].pk
        )
        return tagged_item


class BulkTaggedSerializer(ContentTypeMixin, serializers.ModelSerializer):
    content_type = ContentTypeNaturalKeyField(label='内容类型')
    object_id = serializers.IntegerField(label='对象主键', min_value=0, required=True)
    tags = serializers.CharField(label='标签', allow_blank=True, help_text='多标签使用空格、逗号或分号分隔。')

    class Meta:
        model = TaggedItem
        fields = ['content_type', 'object_id', 'tags']

    def validate_tags(self, value):
        return string_split(value)

    def validate(self, attrs):
        # 多重继承中的父类均有相同的子方法按照`__mro__`顺序查找并执行
        attrs = super().validate(attrs)

        instance = attrs['instance']
        request = self.context['request']
        if not (hasattr(instance, 'is_owned') and instance.is_owned(request.user)):
            raise ValidationError(Messages.INSTANCE_NOT_ALLOWED.format(attrs['content_type'], instance.pk))

        return attrs

    def bulk_create(self):
        with transaction.atomic():
            ret = list(map(itemgetter(0), [
                TaggedItem.objects.get_or_create(
                    tag=tag,
                    content_type=self.validated_data['content_type'],
                    object_id=self.validated_data['instance'].pk
                ) for tag in map(itemgetter(0), [Tag.objects.get_or_create(name=tag) for tag in self.validated_data['tags']])
            ]))
        return ret

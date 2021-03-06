import re
import functools

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, ReadOnlyField, RegexField
from rest_framework.relations import RelatedField
from rest_framework.validators import UniqueValidator

from commons.constants import Messages
from commons.fields.phonenumber import PhoneNumber
from commons.utils import timesince


CaptchaField = functools.partial(RegexField, regex=re.compile(r'^\d{6}$'))


class TimesinceField(ReadOnlyField):

    def to_representation(self, value):
        return timesince(value)


class PhoneField(CharField):
    default_error_messages = {'invalid': 'Enter a valid phone number.'}

    def to_internal_value(self, data):
        phone_number = PhoneNumber.to_python(data)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages['invalid'])
        return phone_number


class PasswordField(CharField):

    def __init__(self, **kwargs):
        kwargs.setdefault('style', {})
        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True
        super().__init__(**kwargs)


class ContentTypeNaturalKeyField(CharField):
    default_error_messages = {
        'invalid': 'Must be a valid natural key format `app_label.model`. Your value: `{value}`.',
        'not_exist': 'Content type for natural key `{value}` does not exist.'
    }

    def to_internal_value(self, data):
        try:
            app_label, model = data.split('.')
        except ValueError:
            self.fail('invalid', value=data)

        try:
            ct = ContentType.objects.get_by_natural_key(app_label, model)
        except ContentType.DoesNotExist:
            self.fail('not_exist', value=data)

        return ct

    def to_representation(self, value):
        return f'{value.app_label}.{value.model}'


class GenericRelatedField(RelatedField):

    def __init__(self, action_models, **kwargs):
        self.action_models = action_models
        super().__init__(**kwargs)

    def to_representation(self, value):
        for model_path, configuration in getattr(settings, self.action_models, {}).items():
            serializer_path = configuration.get('serializer')

            if not serializer_path:
                return str(value)

            app_label, model_name = model_path.split('.')
            model_class = apps.get_model(app_label, model_name)
            serializer_class = import_string(serializer_path)

            if isinstance(value, model_class):
                return serializer_class(instance=value, context=self.context).data

        return str(value)


class CheckContentTypeMixin:

    def validate(self, attrs):
        content_type = attrs['content_type']
        action_claim = getattr(self.fields.get('content_object'), 'action_models', None)

        model_path = f'{content_type.app_label}.{content_type.model}'
        if action_claim is not None and model_path not in getattr(settings, action_claim, {model_path: None}):
            raise ValidationError({'content_type': Messages.CONTENT_TYPE_NOT_ALLOWED})

        try:
            obj = content_type.get_object_for_this_type(pk=attrs['object_id'])
        except ObjectDoesNotExist:
            raise ValidationError({'object_id': Messages.OBJECT_NOT_FOUND})
        else:
            attrs['instance'] = obj

        return attrs


class DynamicFieldsMixin:

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        include = list(kwargs.pop('include', []))
        exclude = list(kwargs.pop('exclude', []))
        expand = list(kwargs.pop('expand', []))

        super().__init__(*args, **kwargs)
        self.parent = parent

        include = include or self._get_query_param_values('include')
        exclude = exclude or self._get_query_param_values('exclude')
        expand = expand or self._get_query_param_values('expand')

        for field_name in self._get_remove_field_names(include, exclude, expand):
            self.fields.pop(field_name)

    def _get_remove_field_names(self, include, exclude, expand):
        all_fields = set(self.fields)
        expandable_fields = set(getattr(self.Meta, 'expandable_fields', []))
        default_fields = all_fields - expandable_fields

        remove = []
        # ????????????
        include and remove.extend(default_fields - set(include))
        # ????????????
        exclude and remove.extend(exclude)
        # ????????????
        remove.extend(expandable_fields - set(expand))

        # ??????????????????????????????
        return list(set(remove) & all_fields)

    def _get_query_param_values(self, field):
        if self.parent is not None:
            return []

        if not hasattr(self, 'context') or 'request' not in self.context:
            return []

        values = self.context['request'].query_params.get(field, [])
        return values and values.split(',')


class UniqueFieldsMixin:

    def __init__(self, *args, **kwargs):
        self.omit_fields = list(kwargs.pop('omit_fields', []))
        super().__init__(*args, **kwargs)

    def get_fields(self):
        fields = super().get_fields()
        for field_name, field in fields.items():
            if field_name in self.omit_fields:
                field.validators = [v for v in field.validators if not isinstance(v, UniqueValidator)]
        return fields

from django.core import checks
from django.db.models.fields import CharField
from django.utils.encoding import force_str

from commons.fields import forms
from commons.fields.phonenumber import PhoneNumber


class PhoneDescriptor:
    # 描述符：https://docs.python.org/zh-cn/3/howto/descriptor.html

    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # The instance dict contains whatever was originally assigned in __set__
        if self.field.name in instance.__dict__:
            value = instance.__dict__[self.field.name]
        else:
            instance.refresh_from_db(fields=[self.field.name])
            value = getattr(instance, self.field.name)

        return value

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = PhoneNumber.to_python(value, region=self.field.region)


class PhoneField(CharField):
    attr_class = PhoneNumber
    descriptor_class = PhoneDescriptor
    default_validators = [PhoneNumber.validate_phone]
    description = 'Phone number'

    def __init__(self, *args, region=None, **kwargs):
        kwargs.setdefault('max_length', 128)
        super().__init__(*args, **kwargs)
        self._region = region

    @property
    def region(self):
        return self._region or PhoneNumber.DEFAULT_REGION

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        errors.extend(self._check_region())
        return errors

    def _check_region(self):
        try:
            PhoneNumber.validate_region(self.region)
        except ValueError as e:
            return [checks.Error(force_str(e), obj=self)]
        return []

    def get_prep_value(self, value):
        parsed_value = PhoneNumber.to_python(value)
        return super().get_prep_value(str(parsed_value))

    def contribute_to_class(self, cls, name, *args, **kwargs):
        super().contribute_to_class(cls, name, *args, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['region'] = self.region
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.PhoneField,
            'region': self.region
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

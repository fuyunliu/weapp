from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, Field

from commons.fields.phonenumber import PhoneNumber
from commons.utils import timesince


class TimesinceField(Field):
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
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})
        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True
        super().__init__(*args, **kwargs)


class DigitsField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs['validators'] = [RegexValidator(regex=r'^\d{6}$', message='Please enter 6 digits.')]
        super().__init__(*args, **kwargs)

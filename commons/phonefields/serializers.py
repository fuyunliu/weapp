from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .phonenumber import PhoneNumber


class PhoneField(serializers.CharField):
    default_error_messages = {'invalid': _('Enter a valid phone number.')}

    def to_internal_value(self, data):
        phone_number = PhoneNumber.to_python(data)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages['invalid'])
        return phone_number

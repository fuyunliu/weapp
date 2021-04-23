from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.fields import CharField

from commons.fields.phonenumber import PhoneNumber


class PhoneField(CharField):
    default_validators = [PhoneNumber.validate_phone]

    def __init__(self, *args, region=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.input_type = 'tel'

        PhoneNumber.validate_region(region)
        self.region = region

        self.error_messages.setdefault('invalid', 'Enter a valid phone number.')

    def to_python(self, value):
        phone_number = PhoneNumber.to_python(value, region=self.region)

        # 号码允许为空
        if phone_number.raw_input in validators.EMPTY_VALUES:
            return self.empty_value

        # 不为空时不能为非法号码
        if not phone_number.is_valid():
            raise ValidationError(self.error_messages['invalid'])

        return phone_number

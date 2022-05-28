import phonenumbers
from django.conf import settings
from django.core.exceptions import ValidationError
from phonenumbers.phonenumberutil import region_code_for_number
from phonenumbers.util import unicod


class PhoneNumber(phonenumbers.PhoneNumber):
    # https://github.com/stefanfoulis/django-phonenumber-field

    DEFAULT_REGION = settings.OAUTH.get('PHONENUMBER_DEFAULT_REGION')

    @classmethod
    def from_string(cls, phone_number, region=None):
        numobj = cls()
        phonenumbers.parse(
            number=phone_number,
            region=region or cls.DEFAULT_REGION,
            keep_raw_input=True,
            numobj=numobj
        )
        return numobj

    @classmethod
    def to_python(cls, value, region=None):
        if isinstance(value, str):
            try:
                phone_number = cls.from_string(phone_number=value, region=region)
            except phonenumbers.NumberParseException:
                phone_number = cls(raw_input=value)
        elif isinstance(value, cls):
            phone_number = value
        elif isinstance(value, phonenumbers.PhoneNumber):
            phone_number = cls()
            phone_number.merge_from(value)
        else:
            phone_number = cls(raw_input='')

        return phone_number

    @staticmethod
    def validate_region(region):
        if region is not None and region not in phonenumbers.shortdata._AVAILABLE_REGION_CODES:
            raise ValueError(f"{region} is not a valid region code.")

    @staticmethod
    def validate_phone(value):
        phone_number = PhoneNumber.to_python(value)
        if not phone_number.is_valid():
            raise ValidationError(
                message='The phone number entered is not valid.',
                code='invalid_phone_number'
            )

    def __str__(self):
        if self.is_valid():
            return self.format_as(phonenumbers.PhoneNumberFormat.E164)
        else:
            return str(self.raw_input)

    def __repr__(self):
        if self.is_valid():
            return unicod(
                f'{type(self).__name__}(country_code={self.country_code}, '
                f'national_number={self.national_number}, '
                f'region_code={self.region_code})'
            )
        else:
            return unicod(
                f'Invalid {type(self).__name__}(raw_input={self.raw_input})'
            )

    def __len__(self):
        return len(str(self))

    def __eq__(self, other):
        other = self.to_python(other)
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def is_valid(self):
        return phonenumbers.is_valid_number(self)

    def format_as(self, num_format):
        return phonenumbers.format_number(self, num_format)

    @property
    def region_code(self):
        return region_code_for_number(self)

    @property
    def as_international(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    @property
    def as_e164(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.E164)

    @property
    def as_national(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.NATIONAL)

    @property
    def as_rfc3966(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.RFC3966)

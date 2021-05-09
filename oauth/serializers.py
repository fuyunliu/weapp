from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, update_last_login
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from commons import utils
from commons.constants import Messages, CacheKeySet
from commons.fields.serializers import (
    DigitsField,
    PhoneField,
    PasswordField,
    TimesinceField
)
from oauth import login_user, user_can_authenticate
from oauth.email import DigitsEmail
from oauth.models import Profile

UserModel = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['nickname', 'gender', 'birthday', 'location', 'about_me', 'avatar_hash']
        read_only_fields = ['nickname', 'avatar_hash']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    date_joined = TimesinceField(read_only=True)
    profile = serializers.HyperlinkedRelatedField(lookup_field='pk', view_name='profile-detail', read_only=True)
    nickname = serializers.ReadOnlyField(source='profile.nickname')
    articles = serializers.HyperlinkedRelatedField(many=True, view_name='article-detail', read_only=True)

    class Meta:
        model = UserModel
        fields = ['url', 'username', 'nickname', 'email', 'phone', 'first_name', 'last_name', 'date_joined', 'articles', 'profile']
        read_only_fields = ['username', 'email', 'phone']


class UserCreateSerializer(serializers.ModelSerializer):
    password = PasswordField(label='密码')
    re_password = PasswordField(label='确认密码')

    class Meta:
        model = UserModel
        fields = ['username', 'email', 'phone', 'password', 're_password']
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'phone': {'required': True, 'allow_blank': False}
        }

    def validate_username(self, value):
        if UserModel.objects.filter(username=value).exists():
            raise ValidationError(Messages.USERNAME_EXIST)
        return value

    def validate_email(self, value):
        if UserModel.objects.filter(email=value).exists():
            raise ValidationError(Messages.EMAIL_EXIST)
        return value

    def validate_phone(self, value):
        if UserModel.objects.filter(phone=value).exists():
            raise ValidationError(Messages.PHONE_EXIST)
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except serializers.DjangoValidationError as e:
            errors = serializers.as_serializer_error(e)
            raise ValidationError(errors[api_settings.NON_FIELD_ERRORS_KEY])
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('re_password'):
            raise ValidationError({'re_password': Messages.PASSWORD_MISMATCH})
        return attrs

    def create(self, validated_data):
        user = self.perform_create(validated_data)
        return user

    def perform_create(self, validated_data):
        user = UserModel.objects.create_user(**validated_data)
        return user


class UserDeleteSerializer(serializers.Serializer):
    password = PasswordField()

    def validate_password(self, value):
        if not self.instance.check_password(value):
            raise ValidationError(Messages.WRONG_PASSWORD)
        return value


class ActivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['is_active']


class SendPhoneDigitsSerializer(serializers.Serializer):
    phone = PhoneField()
    tape = serializers.ChoiceField(choices=['gettoken', 'setpasswd', 'setemail', 'setphone'])

    def validate(self, attrs):
        digits = utils.get_random_number()
        key = CacheKeySet.PHONE_DIGITS.format(**attrs)
        timeout = settings.ACCESS_DIGITS_LIFETIME.total_seconds()
        cache.set(key, digits, timeout=timeout)
        print(f'Send phone digits: {digits}')
        return {}


class SendEmailDigitsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    tape = serializers.ChoiceField(choices=['gettoken', 'setpasswd', 'setemail', 'setphone'])

    def validate(self, attrs):
        digits = utils.get_random_number()
        key = CacheKeySet.EMAIL_DIGITS.format(**attrs)
        timeout = settings.ACCESS_DIGITS_LIFETIME.total_seconds()
        cache.set(key, digits, timeout=timeout)
        context = {'digits': digits}
        DigitsEmail(context=context).send([attrs['email']])
        return {}


class SetUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username']

    def validate_username(self, value):
        if UserModel.objects.filter(username=value).exists():
            raise ValidationError(Messages.USERNAME_EXIST)
        return value

    def validate(self, attrs):
        allowed_time = settings.USERNAME_MODIFY_TIMEDELTA - (timezone.now() - self.instance.name_mtime)
        if allowed_time.total_seconds() > 0:
            raise ValidationError(Messages.NEW_USERNAME.format(allowed_time.days))
        return attrs


class SetNicknameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['nickname']

    def validate_nickname(self, value):
        if Profile.objects.filter(username=value).exists():
            raise ValidationError(Messages.NICKNAME_EXIST)
        return value

    def validate(self, attrs):
        profile = self.instance.profile
        allowed_time = settings.NICKNAME_MODIFY_TIMEDELTA - (timezone.now() - profile.nick_mtime)
        if allowed_time.total_seconds() > 0:
            raise ValidationError(Messages.NEW_NICKNAME.format(allowed_time.days))
        return attrs


class SetPasswordSerializer(serializers.Serializer):
    new_password = PasswordField()
    re_password = PasswordField()
    digits = DigitsField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs.pop('re_password'):
            raise ValidationError({'re_password': Messages.PASSWORD_MISMATCH})

        digits = attrs.pop('digits')
        key_ed = CacheKeySet.EMAIL_DIGITS.format(email=self.instance.email, tape='setpasswd')
        key_pd = CacheKeySet.PHONE_DIGITS.format(phone=self.instance.phone, tape='setpasswd')
        value = cache.get(key_ed) or cache.get(key_pd)
        if value is None or value != digits:
            raise ValidationError({'digits': Messages.WRONG_DIGITS})

        try:
            validate_password(attrs['new_password'])
        except serializers.DjangoValidationError as e:
            errors = serializers.as_serializer_error(e)
            raise ValidationError({'new_password': errors[api_settings.NON_FIELD_ERRORS_KEY]})

        return attrs

class SetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    digits = DigitsField()

    def validate_email(self, value):
        if UserModel.objects.filter(email=value).exists():
            raise ValidationError(Messages.EMAIL_EXIST)
        return value

    def validate(self, attrs):
        digits = attrs.pop('digits')
        key = CacheKeySet.EMAIL_DIGITS.format(email=attrs['email'], tape='setemail')
        value = cache.get(key)
        if value is None or value != digits:
            raise ValidationError({'digits': Messages.WRONG_DIGITS})
        return attrs


class SetPhoneSerializer(serializers.Serializer):
    phone = PhoneField()
    digits = DigitsField()

    def validate_phone(self, value):
        if UserModel.objects.filter(phone=value).exists():
            raise ValidationError(Messages.PHONE_EXIST)
        return value

    def validate(self, attrs):
        digits = attrs.pop('digits')
        key = CacheKeySet.PHONE_DIGITS.format(phone=attrs['phone'], tape='setphone')
        value = cache.get(key)
        if value is None or value != digits:
            raise ValidationError({'digits': Messages.WRONG_DIGITS})
        return attrs


class PhoneAndDigitsSerializer(serializers.Serializer):
    phone = PhoneField()
    digits = DigitsField()

    default_error_messages = {
        'inactive_user': Messages.USER_INACTIVE
    }

    def validate(self, attrs):
        digits = attrs.pop('digits')
        user, _ = UserModel.objects.get_or_create(**attrs)
        if not user_can_authenticate(user):
            self.fail('inactive_user')

        key = CacheKeySet.PHONE_DIGITS.format(phone=attrs['phone'], tape='gettoken')
        value = cache.get(key)
        if value is None or value != digits:
            raise ValidationError({'digits': Messages.WRONG_DIGITS})

        data = {}
        request = self.context['request']
        token = login_user(request, user)
        data['access'] = str(token)
        update_last_login(None, user)
        return data


class EmailAndDigitsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    digits = DigitsField()

    default_error_messages = {
        'inactive_user': Messages.USER_INACTIVE
    }

    def validate(self, attrs):
        digits = attrs.pop('digits')
        user, _ = UserModel.objects.get_or_create(**attrs)
        if not user_can_authenticate(user):
            self.fail('inactive_user')

        key = CacheKeySet.EMAIL_DIGITS.format(email=attrs['email'], tape='gettoken')
        value = cache.get(key)
        if value is None or digits != value:
            raise ValidationError({'digits': Messages.WRONG_DIGITS})

        data = {}
        request = self.context['request']
        token = login_user(request, user)
        data['access'] = str(token)
        update_last_login(None, user)
        return data


class PhoneAndPasswordSerializer(serializers.Serializer):
    phone = PhoneField()
    password = PasswordField()

    default_error_messages = {
        'user_not_exist': Messages.USER_NOT_EXIST,
        'inactive_user': Messages.USER_INACTIVE
    }

    def validate(self, attrs):
        password = attrs.pop('password')
        user = UserModel.objects.filter(**attrs).first()
        if user is None:
            self.fail('user_not_exist')
        if not user.check_password(password):
            raise ValidationError({'password': Messages.WRONG_PASSWORD})
        if not user_can_authenticate(user):
            self.fail('inactive_user')

        request = self.context['request']
        user = authenticate(request=request, **attrs, password=password)
        data = {}
        token = login_user(request, user)
        data['access'] = str(token)
        update_last_login(None, user)
        return data



class EmailAndPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = PasswordField()

    default_error_messages = {
        'user_not_exist': Messages.USER_NOT_EXIST,
        'inactive_user': Messages.USER_INACTIVE
    }

    def validate(self, attrs):
        password = attrs.pop('password')
        user = UserModel.objects.filter(**attrs).first()
        if user is None:
            self.fail('user_not_exist')
        if not user.check_password(password):
            raise ValidationError({'password': Messages.WRONG_PASSWORD})
        if not user_can_authenticate(user):
            self.fail('inactive_user')

        request = self.context['request']
        user = authenticate(request=request, **attrs, password=password)
        data = {}
        token = login_user(request, user)
        data['access'] = str(token)
        update_last_login(None, user)
        return data


class UsernameAndPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = PasswordField()

    default_error_messages = {
        'user_not_exist': Messages.USER_NOT_EXIST,
        'inactive_user': Messages.USER_INACTIVE
    }

    def validate(self, attrs):
        password = attrs.pop('password')
        user = UserModel.objects.filter(**attrs).first()
        if user is None:
            self.fail('user_not_exist')
        if not user.check_password(password):
            raise ValidationError({'password': Messages.WRONG_PASSWORD})
        if not user_can_authenticate(user):
            self.fail('inactive_user')

        request = self.context['request']
        user = authenticate(request=request, **attrs, password=password)
        data = {}
        token = login_user(request, user)
        data['access'] = str(token)
        update_last_login(None, user)
        return data

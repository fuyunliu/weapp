from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, update_last_login
from django.core.cache import cache
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
    profile = ProfileSerializer()

    class Meta:
        model = UserModel
        fields = ['url', 'username', 'email', 'phone', 'date_joined', 'profile']
        read_only_fields = ['username', 'email', 'phone']


class UserCreateSerializer(serializers.ModelSerializer):
    digits = DigitsField()

    default_error_messages = {
        'email_phone': Messages.EMAIL_PHONE
    }

    class Meta:
        model = UserModel
        fields = ['email', 'phone', 'digits']

    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        # digits = attrs.pop('digits')
        if not any((email, phone)):
            self.fail('email_phone')
        return attrs

    def create(self, validated_data):
        user = self.perform_create(validated_data)
        return user

    def perform_create(self, validated_data):
        user_model = self.Meta.model
        user = user_model.objects.get_or_create(**validated_data)
        return user


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

    def validate(self, attrs):
        view = self.context['view']
        user = view.get_object()
        allowed_time = settings.USERNAME_MODIFY_TIMEDELTA - (timezone.now() - user.name_mtime)
        if allowed_time.total_seconds() > 0:
            raise ValidationError(Messages.NEW_USERNAME.format(allowed_time.days))
        return attrs


class SetNicknameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['nickname']

    def validate(self, attrs):
        view = self.context['view']
        user = view.get_object()
        profile = user.profile
        allowed_time = settings.NICKNAME_MODIFY_TIMEDELTA - (timezone.now() - profile.nick_mtime)
        if allowed_time.total_seconds() > 0:
            raise ValidationError(Messages.NEW_NICKNAME.format(allowed_time.days))
        return attrs


class SetPasswordSerializer(serializers.Serializer):
    password = PasswordField()
    re_password = PasswordField()
    digits = DigitsField()

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('re_password'):
            raise ValidationError({'re_password': Messages.PASSWORD_MISMATCH})
        digits = attrs.pop('digits')
        view = self.context['view']
        user = view.get_object()
        key_ed = CacheKeySet.EMAIL_DIGITS.format(email=user.email, tape='setpasswd')
        key_pd = CacheKeySet.PHONE_DIGITS.format(phone=user.phone, tape='setpasswd')
        value = cache.get(key_ed) or cache.get(key_pd)
        if value is None or value != digits:
            raise ValidationError({'digits': Messages.WRONG_DIGITS})
        return attrs

class SetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    digits = DigitsField()

    def validate(self, attrs):
        digits = attrs.pop('digits')

        if UserModel.objects.filter(**attrs).exists():
            raise ValidationError({'email': Messages.EMAIL_EXIST})

        key = CacheKeySet.EMAIL_DIGITS.format(email=attrs['email'], tape='setemail')
        value = cache.get(key)
        if value is None or value != digits:
            raise ValidationError({'digits': Messages.WRONG_DIGITS})
        return attrs


class SetPhoneSerializer(serializers.Serializer):
    phone = PhoneField()
    digits = DigitsField()

    def validate(self, attrs):
        digits = attrs.pop('digits')

        if UserModel.objects.filter(**attrs).exists():
            raise ValidationError({'phone': Messages.PHONE_EXIST})

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

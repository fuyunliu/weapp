from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, update_last_login
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from oauth import login_user, user_can_authenticate
from oauth.models import Profile
from oauth.email import DigitsEmail
from commons import utils
from commons.constants import Messages, CacheKeySet
from commons.fields.serializers import (
    DigitsField,
    PhoneField,
    PasswordField,
    TimesinceField
)

UserModel = get_user_model()


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
    password1 = PasswordField()
    digits = DigitsField()

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password1'):
            raise ValidationError({'password1': Messages.PASSWORD_MISMATCH})


        return attrs


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class ActivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['is_active']


class DigitsSerializer(serializers.Serializer):
    digits = DigitsField()

    default_error_messages = {
        'wrong_digits': Messages.WRONG_DIGITS,
        'inactive_user': Messages.USER_INACTIVE
    }

    def validate(self, attrs):
        digits = attrs.pop('digits')
        user, _ = UserModel.objects.get_or_create(**attrs)
        if not user_can_authenticate(user):
            self.fail('inactive_user')

        # validate digits
        email = attrs.get('email')
        phone = attrs.get('phone')
        if email is not None:
            key = CacheKeySet.EMAIL_DIGITS.format(email=email, tape='gettoken')
            value = cache.get(key)
            if value is None or digits != value:
                # self.fail('wrong_digits')
                raise ValidationError({'digits': Messages.WRONG_DIGITS})
        if phone is not None:
            key = CacheKeySet.PHONE_DIGITS.format(phone=phone, tape='gettoken')
            value = cache.get(key)
            if value is None or value != digits:
                # self.fail('wrong_digits')
                raise ValidationError({'digits': Messages.WRONG_DIGITS})

        data = {}
        request = self.context['request']
        token = login_user(request, user)
        data['access'] = str(token)
        update_last_login(None, user)
        return data


class PasswordSerializer(serializers.Serializer):
    password = PasswordField()

    default_error_messages = {
        'user_not_exist': Messages.USER_NOT_EXIST,
        'wrong_password': Messages.WRONG_PASSWORD,
        'inactive_user': Messages.USER_INACTIVE
    }

    def validate(self, attrs):
        password = attrs.pop('password')
        user = UserModel.objects.filter(**attrs).first()
        if user is None:
            self.fail('user_not_exist')
        if not user.check_password(password):
            # self.fail('wrong_password')
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


class SendDigitsSerializer(serializers.Serializer):
    phone = PhoneField(required=False)
    email = serializers.EmailField(required=False)
    # 验证码的用途
    tape = serializers.ChoiceField(choices=['gettoken', 'setpasswd', 'setemail', 'setphone'])

    default_error_messages = {
        'email_phone': Messages.EMAIL_PHONE
    }

    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        tape = attrs['tape']
        if not any((email, phone)):
            self.fail('email_phone')
        digits = utils.get_random_number()
        timeout = settings.ACCESS_DIGITS_LIFETIME
        timeout = timeout.total_seconds()
        if email is not None:
            context = {'digits': digits}
            DigitsEmail(context=context).send([email])
            key = CacheKeySet.EMAIL_DIGITS.format(email=email, tape=tape)
            cache.set(key, digits, timeout=timeout)
        if phone is not None:
            print(f'send phone digits: {digits}')
            key = CacheKeySet.PHONE_DIGITS.format(phone=phone, tape=tape)
            cache.set(key, digits, timeout=timeout)

        return {}


class PhoneAndDigitsSerializer(DigitsSerializer):
    phone = PhoneField()


class EmailAndDigitsSerializer(DigitsSerializer):
    email = serializers.EmailField()


class PhoneAndPasswordSerializer(PasswordSerializer):
    phone = PhoneField()


class EmailAndPasswordSerializer(PasswordSerializer):
    email = serializers.EmailField()


class UsernameAndPasswordSerializer(PasswordSerializer):
    username = serializers.CharField()

from django.conf import settings
from django.core.validators import EmailValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from commons import utils
from commons.constants import Messages, CacheKeySet
from commons.fields.serializers import DynamicFieldsMixin
from commons.fields.serializers import PhoneField, CaptchaField, PasswordField, TimesinceField
from commons.fields.phonenumber import PhoneNumber
from oauth import user_can_authenticate
from oauth.email import CaptchaEmail
from oauth.models import Profile

UserModel = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        exclude = ['nick_mtime']
        read_only_fields = ['user', 'nickname']


class UserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    date_joined = TimesinceField()
    avatar = serializers.ReadOnlyField()
    article_count = serializers.ReadOnlyField()
    post_count = serializers.ReadOnlyField()
    is_following = serializers.ReadOnlyField()
    is_followed = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    follower_count = serializers.ReadOnlyField()
    nickname = serializers.ReadOnlyField(source='profile.nickname')
    about_me = serializers.ReadOnlyField(source='profile.about_me')

    class Meta:
        model = UserModel
        expandable_fields = [
            'article_count', 'post_count', 'following_count',
            'follower_count', 'is_following', 'is_followed',
        ]
        fields = ['id', 'username', 'nickname', 'avatar', 'about_me', 'date_joined'] + expandable_fields
        read_only_fields = ['username']


class UserCreateSerializer(serializers.ModelSerializer):
    password = PasswordField(label='??????')
    password2 = PasswordField(label='????????????')

    class Meta:
        model = UserModel
        fields = ['username', 'email', 'phone', 'password', 'password2']
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
        if attrs['password'] != attrs.pop('password2'):
            raise ValidationError({'password2': Messages.PASSWORD_MISMATCH})
        return attrs

    def create(self, validated_data):
        user = self.perform_create(validated_data)
        return user

    def perform_create(self, validated_data):
        user = UserModel.objects.create_user(**validated_data)
        return user


class UserDestroySerializer(serializers.Serializer):
    password = PasswordField(label='??????')

    def validate_password(self, value):
        if not self.instance.check_password(value):
            raise ValidationError(Messages.WRONG_PASSWORD)
        return value


class SendCaptchaSerializer(serializers.Serializer):
    authname = serializers.CharField(label='??????/?????????')
    tape = serializers.ChoiceField(choices=['gettoken', 'setpasswd', 'setemail', 'setphone'], label='??????')

    default_error_messages = {
        'invalid_authname': Messages.INVALID_AUTHNAME
    }

    def validate(self, attrs):
        tape = attrs['tape']
        authname = attrs['authname']
        captcha = utils.get_random_number()
        timeout = settings.OAUTH['CAPTCHA_LIFETIME'].total_seconds()

        try:
            # ????????? Email
            EmailValidator()(authname)

            # ???????????????
            key = CacheKeySet.CAPTCHA.format(field='email', value=authname, tape=tape)
            cache.set(key, captcha, timeout=timeout)
            CaptchaEmail(context={'tape': tape, 'captcha': captcha}).send([authname])
            return {}
        except serializers.DjangoValidationError:
            pass

        try:
            # ????????? Phone
            PhoneNumber.validate_phone(authname)

            # ???????????????
            key = CacheKeySet.CAPTCHA.format(field='phone', value=authname, tape=tape)
            cache.set(key, captcha, timeout=timeout)
            print(f'Send Captcha: {captcha}')
            return {}
        except serializers.DjangoValidationError:
            pass

        # ????????????????????????
        self.fail('invalid_authname')


class SetUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username']

    def validate_username(self, value):
        if UserModel.objects.filter(username=value).exists():
            raise ValidationError(Messages.USERNAME_EXIST)
        return value

    def validate(self, attrs):
        allowed_time = settings.OAUTH['USERNAME_MODIFY_LIFETIME'] - (timezone.now() - self.instance.name_mtime)
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
        allowed_time = settings.OAUTH['NICKNAME_MODIFY_LIFETIME'] - (timezone.now() - profile.nick_mtime)
        if allowed_time.total_seconds() > 0:
            raise ValidationError(Messages.NEW_NICKNAME.format(allowed_time.days))
        return attrs


class SetPasswordSerializer(serializers.Serializer):
    new_password = PasswordField(label='?????????')
    new_password2 = PasswordField(label='???????????????')
    captcha = CaptchaField(label='?????????')

    def validate(self, attrs):
        if attrs['new_password'] != attrs.pop('new_password2'):
            raise ValidationError({'new_password2': Messages.PASSWORD_MISMATCH})

        captcha = attrs.pop('captcha')
        ekey = CacheKeySet.CAPTCHA.format(field='email', value=self.instance.email, tape='setpasswd')
        pkey = CacheKeySet.CAPTCHA.format(field='phone', value=self.instance.phone, tape='setpasswd')
        value = cache.get(ekey) or cache.get(pkey)
        if value is None or value != captcha:
            raise ValidationError({'captcha': Messages.WRONG_CAPTCHA})

        try:
            validate_password(attrs['new_password'])
        except serializers.DjangoValidationError as e:
            errors = serializers.as_serializer_error(e)
            raise ValidationError({'new_password': errors[api_settings.NON_FIELD_ERRORS_KEY]})

        return attrs


class SetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(label='?????????')
    captcha = CaptchaField(label='?????????')

    def validate_email(self, value):
        if UserModel.objects.filter(email=value).exists():
            raise ValidationError(Messages.EMAIL_EXIST)
        return value

    def validate(self, attrs):
        captcha = attrs.pop('captcha')
        key = CacheKeySet.CAPTCHA.format(field='email', value=attrs['email'], tape='setemail')
        value = cache.get(key)
        if value is None or value != captcha:
            raise ValidationError({'phone_code': Messages.WRONG_CAPTCHA})
        return attrs


class SetPhoneSerializer(serializers.Serializer):
    phone = PhoneField(label='????????????')
    captcha = CaptchaField(label='?????????')

    def validate_phone(self, value):
        if UserModel.objects.filter(phone=value).exists():
            raise ValidationError(Messages.PHONE_EXIST)
        return value

    def validate(self, attrs):
        captcha = attrs.pop('captcha')
        key = CacheKeySet.CAPTCHA.format(field='phone', value=attrs['phone'], tape='setphone')
        value = cache.get(key)
        if value is None or value != captcha:
            raise ValidationError({'phone_code': Messages.WRONG_CAPTCHA})
        return attrs


class CaptchaLoginSerializer(serializers.Serializer):
    authname = serializers.CharField(label='??????/?????????')
    captcha = CaptchaField(label='?????????')

    default_error_messages = {
        'invalid_authname': Messages.INVALID_AUTHNAME,
        'inactive_user': Messages.USER_INACTIVE
    }

    def validate(self, attrs):
        captcha = attrs.pop('captcha')
        authname = attrs['authname']

        user = None
        try:
            # ????????? Email
            EmailValidator()(authname)

            # ???????????????
            key = CacheKeySet.CAPTCHA.format(field='email', value=authname, tape='gettoken')
            value = cache.get(key)
            if value is None or value != captcha:
                raise ValidationError({'captcha': Messages.WRONG_CAPTCHA})

            # ?????????????????????????????????
            user, _ = UserModel.objects.get_or_create(email=authname)
        except serializers.DjangoValidationError:
            pass

        try:
            # ????????? Phone
            PhoneNumber.validate_phone(authname)

            # ???????????????
            key = CacheKeySet.CAPTCHA.format(field='phone', value=authname, tape='gettoken')
            value = cache.get(key)
            if value is None or value != captcha:
                raise ValidationError({'captcha': Messages.WRONG_CAPTCHA})

            # ?????????????????????????????????
            user, _ = UserModel.objects.get_or_create(phone=authname)
        except serializers.DjangoValidationError:
            pass

        if user is None:
            self.fail('invalid_authname')
        if not user_can_authenticate(user):
            self.fail('inactive_user')

        attrs['instance'] = user
        return attrs


class PasswordLoginSerializer(serializers.Serializer):
    authname = serializers.CharField(label='?????????/??????/?????????')
    password = PasswordField(label='??????')

    default_error_messages = {
        'user_not_exist': Messages.USER_NOT_FOUND,
        'inactive_user': Messages.USER_INACTIVE
    }

    def validate(self, attrs):
        password = attrs.pop('password')
        authname = attrs['authname']

        user = None
        try:
            # ????????? Email
            EmailValidator()(authname)

            # ????????????
            user = UserModel.objects.filter(email=authname).first()
        except serializers.DjangoValidationError:
            pass

        try:
            # ????????? Phone
            PhoneNumber.validate_phone(authname)

            # ????????????
            user = UserModel.objects.filter(phone=authname).first()
        except serializers.DjangoValidationError:
            pass

        # ?????????????????????
        if user is None:
            user = UserModel.objects.filter(username=authname).first()

        if user is None:
            self.fail('user_not_exist')
        if not user.check_password(password):
            raise ValidationError({'password': Messages.WRONG_PASSWORD})
        if not user_can_authenticate(user):
            self.fail('inactive_user')

        attrs['instance'] = user
        return attrs

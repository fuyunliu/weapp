from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from commons import utils
from commons.constants import Messages, CacheKeySet
from commons.fields.serializers import PhoneField, PhoneCodeField, PasswordField, TimesinceField
from oauth import login_user, logout_user, user_can_authenticate
from oauth.email import PhoneCodeEmail
from oauth.models import Profile

UserModel = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class ProfileSerializer(serializers.ModelSerializer):
    # user = serializers.HyperlinkedIdentityField(view_name='user-detail', read_only=True)
    class Meta:
        model = Profile
        fields = ['url', 'nickname', 'gender', 'birthday', 'location', 'about_me', 'avatar_hash']
        read_only_fields = ['nickname', 'avatar_hash']


class UserSerializer(serializers.ModelSerializer):
    date_joined = TimesinceField()
    # nickname = serializers.ReadOnlyField(source='profile.nickname')
    # profile = serializers.HyperlinkedRelatedField(view_name='profile-detail', read_only=True)
    # articles = serializers.HyperlinkedRelatedField(many=True, view_name='article-detail', read_only=True)

    class Meta:
        model = UserModel
        fields = ['url', 'username', 'email', 'phone', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['username', 'email', 'phone']


class UserCreateSerializer(serializers.ModelSerializer):
    password = PasswordField(label='密码')
    password2 = PasswordField(label='确认密码')

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
    password = PasswordField()

    def validate_password(self, value):
        if not self.instance.check_password(value):
            raise ValidationError(Messages.WRONG_PASSWORD)
        return value

    def validate(self, attrs):
        request = self.context['request']
        if self.instance == request.user:
            logout_user(request)
        return attrs


class PhoneCodeSerializer(serializers.Serializer):
    phone = PhoneField()
    tape = serializers.ChoiceField(choices=['gettoken', 'setpasswd', 'setemail', 'setphone'])

    def validate(self, attrs):
        phone_code = utils.get_random_number()
        key = CacheKeySet.PHONE_CODE.format(field='phone', value=attrs['phone'], tape=attrs['tape'])
        timeout = settings.ACCESS_CODE_LIFETIME.total_seconds()
        cache.set(key, phone_code, timeout=timeout)
        print(f'Send phone code: {phone_code}')
        return {}


class EmailCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    tape = serializers.ChoiceField(choices=['gettoken', 'setpasswd', 'setemail', 'setphone'])

    def validate(self, attrs):
        phone_code = utils.get_random_number()
        key = CacheKeySet.PHONE_CODE.format(field='email', value=attrs['email'], tape=attrs['tape'])
        timeout = settings.ACCESS_CODE_LIFETIME.total_seconds()
        cache.set(key, phone_code, timeout=timeout)
        context = {'digits': phone_code}
        PhoneCodeEmail(context=context).send([attrs['email']])
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
    phone_code = PhoneCodeField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs.pop('re_password'):
            raise ValidationError({'re_password': Messages.PASSWORD_MISMATCH})

        phone_code = attrs.pop('phone_code')
        ekey = CacheKeySet.PHONE_CODE.format(field='email', value=self.instance.email, tape='setpasswd')
        pkey = CacheKeySet.PHONE_CODE.format(field='phone', value=self.instance.phone, tape='setpasswd')
        value = cache.get(ekey) or cache.get(pkey)
        if value is None or value != phone_code:
            raise ValidationError({'phone_code': Messages.WRONG_PHONE_CODE})

        try:
            validate_password(attrs['new_password'])
        except serializers.DjangoValidationError as e:
            errors = serializers.as_serializer_error(e)
            raise ValidationError({'new_password': errors[api_settings.NON_FIELD_ERRORS_KEY]})

        return attrs


class SetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_code = PhoneCodeField()

    def validate_email(self, value):
        if UserModel.objects.filter(email=value).exists():
            raise ValidationError(Messages.EMAIL_EXIST)
        return value

    def validate(self, attrs):
        phone_code = attrs.pop('phone_code')
        key = CacheKeySet.PHONE_CODE.format(field='email', value=attrs['email'], tape='setemail')
        value = cache.get(key)
        if value is None or value != phone_code:
            raise ValidationError({'phone_code': Messages.WRONG_PHONE_CODE})
        return attrs


class SetPhoneSerializer(serializers.Serializer):
    phone = PhoneField()
    phone_code = PhoneCodeField()

    def validate_phone(self, value):
        if UserModel.objects.filter(phone=value).exists():
            raise ValidationError(Messages.PHONE_EXIST)
        return value

    def validate(self, attrs):
        phone_code = attrs.pop('phone_code')
        key = CacheKeySet.PHONE_CODE.format(field='phone', value=attrs['phone'], tape='setphone')
        value = cache.get(key)
        if value is None or value != phone_code:
            raise ValidationError({'phone_code': Messages.WRONG_PHONE_CODE})
        return attrs


class PhoneAndCodeSerializer(serializers.Serializer):
    phone = PhoneField()
    phone_code = PhoneCodeField()

    default_error_messages = {
        'inactive_user': Messages.USER_INACTIVE
    }

    def validate(self, attrs):
        phone_code = attrs.pop('phone_code')
        user, _ = UserModel.objects.get_or_create(**attrs)
        if not user_can_authenticate(user):
            self.fail('inactive_user')

        key = CacheKeySet.PHONE_CODE.format(field='phone', value=attrs['phone'], tape='gettoken')
        value = cache.get(key)
        if value is None or value != phone_code:
            raise ValidationError({'digits': Messages.WRONG_PHONE_CODE})

        data = {}
        request = self.context['request']
        token = login_user(request, user)
        data['access'] = str(token)
        update_last_login(None, user)
        return data


class EmailAndCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_code = PhoneCodeField()

    default_error_messages = {
        'inactive_user': Messages.USER_INACTIVE
    }

    def validate(self, attrs):
        phone_code = attrs.pop('phone_code')
        user, _ = UserModel.objects.get_or_create(**attrs)
        if not user_can_authenticate(user):
            self.fail('inactive_user')

        key = CacheKeySet.PHONE_CODE.format(field='email', value=attrs['email'], tape='gettoken')
        value = cache.get(key)
        if value is None or value != phone_code:
            raise ValidationError({'phone_code': Messages.WRONG_PHONE_CODE})

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
        'user_not_exist': Messages.USER_NOT_FOUND,
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
        'user_not_exist': Messages.USER_NOT_FOUND,
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
        'user_not_exist': Messages.USER_NOT_FOUND,
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

# from django.core.cache import cache
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, update_last_login
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from oauth import login_user, user_can_authenticate
from commons.constants import Messages
from commons.fields.serializers import (
    DigitsField,
    PhoneField,
    PasswordField,
    TimesinceField
)

UserModel = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    date_joined = TimesinceField(read_only=True)

    class Meta:
        model = UserModel
        fields = ['url', 'username', 'email', 'phone', 'date_joined']


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
        digits = attrs.pop('digits')
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
        digits = attrs.pop('digits')  # validate digits
        user, _ = UserModel.objects.get_or_create(**attrs)
        if not user_can_authenticate(user):
            self.fail('inactive_user')
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
            self.fail('wrong_password')
        if not user_can_authenticate(user):
            self.fail('inactive_user')

        request = self.context['request']
        user = authenticate(request=request, **attrs, password=password)
        data = {}
        token = login_user(request, user)
        data['access'] = str(token)
        update_last_login(None, user)
        return data


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

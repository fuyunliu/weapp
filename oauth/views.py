from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import permissions
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response

from commons.permissions import IsMeOrAdmin
from oauth import serializers
from oauth.email import DestroyUserEmail
from oauth.models import Profile
from oauth.tasks import destroy_user

UserModel = get_user_model()


class TokenViewSet(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        token = request.auth
        token.set_exp()
        data = {'access': str(token)}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        serializers.logout_user(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        ctx = {'request': self.request, 'format': self.format_kwarg, 'view': self}
        kwargs.setdefault('context', ctx)
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        data = self.request.data
        if self.request.method == 'POST':
            if 'digits' in data:
                if 'phone' in data:
                    return serializers.PhoneAndDigitsSerializer
                elif 'email' in data:
                    return serializers.EmailAndDigitsSerializer
            elif 'password' in data:
                if 'username' in data:
                    return serializers.UsernameAndPasswordSerializer
                elif 'email' in data:
                    return serializers.EmailAndPasswordSerializer
                elif 'phone' in data:
                    return serializers.PhoneAndPasswordSerializer
            else:
                return serializers.PhoneAndDigitsSerializer
        return serializers.PhoneAndDigitsSerializer


class SendDigitsView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        ctx = {'request': self.request, 'format': self.format_kwarg, 'view': self}
        kwargs.setdefault('context', ctx)
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        data = self.request.data
        if self.request.method == 'POST':
            if 'phone' in data:
                return serializers.SendPhoneDigitsSerializer
            elif 'email' in data:
                return serializers.SendEmailDigitsSerializer
            else:
                return serializers.SendPhoneDigitsSerializer
        return serializers.SendPhoneDigitsSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsMeOrAdmin]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        # 管理员可以看到所有人员，普通用户仅能看到自己
        if self.action == 'list' and not user.is_staff:
            queryset = queryset.filter(pk=user.pk)
        return queryset

    def get_instance(self):
        return self.request.user

    def get_permissions(self):
        action_perms = {
            'create': [permissions.IsAdminUser],
            'activation': [permissions.IsAdminUser]
        }
        self.permission_classes = action_perms.get(self.action, self.permission_classes)
        return super().get_permissions()

    def get_serializer_class(self):
        action_seres = {
            'create': serializers.UserCreateSerializer,
            'destroy': serializers.UserDeleteSerializer,
            'set_username': serializers.SetUsernameSerializer,
            'set_nickname': serializers.SetNicknameSerializer,
            'set_password': serializers.SetPasswordSerializer,
            'set_email': serializers.SetEmailSerializer,
            'set_phone': serializers.SetPhoneSerializer
        }
        return action_seres.get(self.action, self.serializer_class)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_destroy(user)
        DestroyUserEmail(request).send([user.email])
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        destroy_user.apply_async((instance.pk,), eta=timezone.now() + settings.DESTROY_USER_TIMEDELTA, expires=60)

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(['post'], detail=True)
    def activation(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, url_path='set-username')
    def set_username(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user.set_username(username)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, url_path='set-nickname')
    def set_nickname(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        nickname = serializer.validated_data['nickname']
        profile = user.profile
        profile.set_nickname(nickname)
        profile.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, url_path='set-password')
    def set_password(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        user.set_password(password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, url_path='set-email')
    def set_email(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = self.get_object()
        user.email = email
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, url_path='set-phone')
    def set_phone(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        user = self.get_object()
        user.phone = phone
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=True)
    def articles(self, request, *args, **kwargs):
        pass

    @action(methods=['get'], detail=True)
    def pins(self, request, *args, **kwargs):
        pass

    @action(methods=['get'], detail=True)
    def likes(self, request, *args, **kwargs):
        # 使用filter过滤用户喜欢的文章或者想法等等
        # 避免制造过深的URL
        pass

    @action(methods=['get'], detail=True)
    def comments(self, request, *args, **kwargs):
        # 使用filter过滤对文章的评论或者对想法的评论
        pass

    @action(methods=['get'], detail=True)
    def collections(self, request, *args, **kwargs):
        pass

    @action(methods=['get'], detail=True)
    def stars(self, request, *args, **kwargs):
        pass

    @action(methods=['get'], detail=True)
    def fans(self, request, *args, **kwargs):
        pass

    @action(methods=['get'], detail=True)
    def polls(self, request, *args, **kwargs):
        pass


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [permissions.IsAdminUser]

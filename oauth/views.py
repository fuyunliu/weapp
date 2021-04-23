from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, generics, views
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from oauth.serializers import (
    UserSerializer,
    GroupSerializer,
    TokenSerializer,
    PhoneAndDigitsSerializer,
    EmailAndDigitsSerializer,
    PhoneAndPasswordSerializer,
    EmailAndPasswordSerializer,
    UsernameAndPasswordSerializer
)
from commons.permissions import IsMeOrAdmin


class TokenViewSet(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        return Response({'method': 'delete'})

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        data = self.request.data
        if self.request.method == 'POST':
            if 'digits' in data:
                if 'phone' in data:
                    return PhoneAndDigitsSerializer
                elif 'email' in data:
                    return EmailAndDigitsSerializer
            elif 'password' in data:
                if 'username' in data:
                    return UsernameAndPasswordSerializer
                elif 'email' in data:
                    return EmailAndPasswordSerializer
                elif 'phone' in data:
                    return PhoneAndPasswordSerializer
            return PhoneAndDigitsSerializer

        elif self.request.method == 'PUT':
            return EmailAndDigitsSerializer

        return TokenSerializer


    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
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
            'digits': [permissions.AllowAny],
            'activate': [permissions.IsAdminUser]
        }
        self.permission_classes = action_perms.get(self.action, self.permission_classes)
        return super().get_permissions()

    # def get_serializer_class(self):
    #     pass


    @action(['get', 'put', 'patch', 'delete'], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == 'GET':
            return self.retrieve(request, *args, **kwargs)
        elif request.method == 'PUT':
            return self.update(request, *args, **kwargs)
        elif request.method == 'PATCH':
            return self.partial_update(request, *args, **kwargs)
        elif request.method == 'DELETE':
            return self.destroy(request, *args, **kwargs)

    @action(['post'], detail=True)
    def activate(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False)
    def digits(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)



    @action(methods=['post'], detail=True, url_path='send-sms')
    def send_sms(self, request, *args, **kwargs):
        # 需要区分是给自己的手机号发送还是给新手机发送
        # 验证码需要存储三样东西：user_id+phone+code
        # 谁给哪个手机号发送了什么code
        # oauth:users:id:1:phone:+8618701538133.code
        pass


    @action(methods=['post'], detail=True, url_path='send-email')
    def send_email(self, request, *args, **kwargs):
        # 需要区分是给自己的邮箱发送还是给新邮箱发送
        # 验证码需要存储三样东西：user_id+email+code
        # 谁给哪个邮箱发送了什么code
        # oauth:users:id:1:email:920507252@qq.com.code
        pass


    @action(methods=['post'], detail=True, url_path='set-username')
    def set_username(self, request, *args, **kwargs):
        # 不需要code，一年改一次
        pass

    @action(methods=['post'], detail=True, url_path='set-nickname')
    def set_nickname(self, request, *args, **kwargs):
        # 不需要code，一季度改一次
        pass

    @action(methods=['post'], detail=True, url_path='set-password')
    def set_password(self, request, *args, **kwargs):
        # 通过邮箱或手机发送code，验证password和code
        # 直接拼key查找code，找不到或失效则失败
        pass

    @action(methods=['post'], detail=True, url_path='set-email')
    def set_email(self, request, *args, **kwargs):
        # 给新邮件地址发送code
        # 直接拼key查找code，找不到或失效则失败
        pass

    @action(methods=['post'], detail=True, url_path='set-phone')
    def set_phone(self, request, *args, **kwargs):
        # 给新手机发送code
        # 直接拼key查找code，找不到或失效则失败
        pass

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



class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsMeOrAdmin]

    # def permission_denied(self, request, **kwargs):
    #     pass

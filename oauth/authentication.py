from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from oauth.models import TokenUser
from oauth.tokens import AccessToken
from oauth.backends import token_backend
from commons.constants import Messages
from commons.utils import aware_utcnow, make_timestamp


class TokenAuthentication(BaseAuthentication):
    auth_header_type = 'Bearer'
    www_authenticate_realm = 'api'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()

    def authenticate(self, request):
        raw_token = request.raw_token
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token, request)
        user = self.get_model_user(validated_token)
        # 认证成功，刷新请求时间
        request.session['last_seen'] = make_timestamp(aware_utcnow())
        return (user, validated_token)

    def authenticate_header(self, request):
        return f'{self.auth_header_type} realm="{self.www_authenticate_realm}"'

    def get_validated_token(self, raw_token, request):
        try:
            payload = token_backend.get_unverified_payload(raw_token)

            # 用户每次登入生成 token，并将 token_id 记录到 session 中
            # 因为下面的续期规则，避免用户继续使用旧的token
            token_id = payload['jti']
            assert 'token_id' in request.session, Messages.TOKEN_NOT_FOUND
            assert token_id == request.session['token_id'], Messages.TOKEN_MISMATCH

            from_time = payload['iat']  # 签发时间
            expire_time = payload['exp']  # 到期时间
            last_seen = request.session['last_seen']  # 上次请求时间
            current_time = make_timestamp(aware_utcnow())  # 当前请求时间
            elapsed = current_time - last_seen  # 请求时间间隔
            lifetime = expire_time - from_time  # token的有效时长
            # 如果请求时间间隔小于 token 的有效时长，则为 token 续期，以达到长期有效的目的。
            leeway = (current_time - from_time) if elapsed < lifetime else 0
            return AccessToken(raw_token, leeway=leeway)
        except Exception as e:
            raise AuthenticationFailed(str(e))

    def get_model_user(self, validated_token):
        """
        Returns a database user object using the given validated token.
        """
        try:
            user_id = validated_token[settings.USER_ID_CLAIM]
        except KeyError:
            raise AuthenticationFailed(Messages.UNKNOWN_UID)

        try:
            user = self.user_model.objects.get(**{settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(Messages.USER_NOT_FOUND)

        if not user.is_active:
            raise AuthenticationFailed(Messages.USER_INACTIVE)

        return user

    def get_token_user(self, validated_token):
        """
        Returns a stateless user object using the given validated token.
        """
        if settings.USER_ID_CLAIM not in validated_token:
            raise AuthenticationFailed(Messages.UNKNOWN_UID)
        return TokenUser(validated_token)

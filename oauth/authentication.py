from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from commons.constants import Messages
from commons.utils import aware_utcnow, make_timestamp
from oauth.models import TokenUser
from oauth.tokens import AccessToken


class TokenAuthentication(BaseAuthentication):
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        raw_token = request.raw_token
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token, request)
        user = self.get_user(validated_token)

        # 认证成功，记录本次请求时间
        request.session['last_seen'] = make_timestamp(aware_utcnow())

        return user, validated_token

    def authenticate_header(self, request):
        return f'Bearer realm="{self.www_authenticate_realm}"'

    def get_validated_token(self, raw_token, request):
        try:
            # 不校验token获取负载信息
            token = AccessToken(raw_token, verify=False)

            # 每次登入生成新的token，为了使旧的token失效但是不想在后端存储token，将新生成的token_id记录在session中。
            # 每次请求过来时，从负载payload中获取token_id，并和session中的token_id进行对比，不相同则认证失败。
            assert 'token_id' in request.session, Messages.TOKEN_NOT_FOUND
            assert token['jti'] == request.session['token_id'], Messages.TOKEN_MISMATCH

            # 为了给token续期，计算需要给token续期的时长，这个时长叫leeway，也就是允许token过期的时长。
            issue_time = token['iat']  # 签发时间
            expire_time = token['exp']  # 到期时间

            last_seen = request.session['last_seen']  # 上次请求时间
            current_time = make_timestamp(aware_utcnow())  # 当前请求时间

            elapsed = current_time - last_seen  # 请求时间间隔
            lifetime = expire_time - issue_time  # token的有效期

            # 如果请求时间间隔小于token的有效期，则为token续期，以达到长期有效的目的。
            leeway = (current_time - issue_time) if elapsed < lifetime else 0
            # 开始验证token
            token.verify(leeway=leeway)
            return token
        except Exception as e:
            raise AuthenticationFailed(str(e))

    def get_user(self, validated_token):
        """
        Returns a database user object using the given validated token.
        """
        try:
            user_id = validated_token[settings.OAUTH['USER_ID_CLAIM']]
        except KeyError:
            raise AuthenticationFailed(Messages.UNKNOWN_UID)

        user_model = get_user_model()
        try:
            user = user_model.objects.get(**{settings.OAUTH['USER_ID_FIELD']: user_id})
        except user_model.DoesNotExist:
            raise AuthenticationFailed(Messages.USER_NOT_FOUND)

        if not user.is_active:
            raise AuthenticationFailed(Messages.USER_INACTIVE)

        return user


class TokenUserAuthentication(TokenAuthentication):
    def get_user(self, validated_token):
        """
        Returns a stateless user object using the given validated token.
        """
        if settings.OAUTH['USER_ID_CLAIM'] not in validated_token:
            raise AuthenticationFailed(Messages.UNKNOWN_UID)
        return TokenUser(validated_token)

from django.conf import settings
from django.contrib.auth import login, logout
from rest_framework.authentication import get_authorization_header
from oauth.tokens import AccessToken


def login_user(request, user):
    # 这里将token认证和session认证结合
    login(request, user)

    # 生成token并记录token的相关信息
    token = AccessToken.for_user(user)
    request.session['token_id'] = token['jti']
    request.session['last_seen'] = token['iat']
    token[settings.SESSION_COOKIE_NAME] = request.session.session_key

    return token


def logout_user(request):
    # 这里将token认证和session认证结合
    # 清空了session自然也就将token_id清除了
    logout(request)


def user_can_authenticate(user):
    return True if user is not None and user.is_active else False


def get_authorization_token(request):
    auth_header_type = 'Bearer'
    header = get_authorization_header(request)
    try:
        tape, token = header.split()
        if tape.lower() != auth_header_type.lower().encode():
            return None
        return token.decode()
    except ValueError:
        return None

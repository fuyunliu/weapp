import uuid
from django.conf import settings
from django.contrib.auth import login, logout

from oauth.tokens import AccessToken


def login_user(request, user):
    # 这里将token认证和session认证结合
    login(request, user)

    # 生成token并记录token的相关信息
    token = AccessToken.for_user(user)
    request.session['token_id'] = token['jti']
    request.session['last_seen'] = token['iat']
    request.session['_'] = uuid.uuid4().hex
    token[settings.SESSION_COOKIE_NAME] = request.session.session_key

    return token


def logout_user(request):
    # 这里将token认证和session认证结合
    # 清空了session自然也就将token_id清除了
    logout(request)


def user_can_authenticate(user):
    return True if user is not None and user.is_active else False

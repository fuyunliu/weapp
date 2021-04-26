from django.conf import settings
from django.contrib.auth import login, logout, user_logged_in, user_logged_out
from rest_framework.authentication import get_authorization_header
from oauth.tokens import AccessToken


def login_user(request, user):
    token = AccessToken.for_user(user)
    login(request, user)
    request.session['token_id'] = token['jti']
    request.session['last_seen'] = token['iat']
    token[settings.SESSION_COOKIE_NAME] = request.session.session_key
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    return token


def logout_user(request):
    user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
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

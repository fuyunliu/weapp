import hmac

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import force_bytes
from django_redis import get_redis_connection
from rest_framework.authentication import get_authorization_header

from commons.utils import make_timestamp, aware_utcnow
from oauth.tokens import AccessToken


def get_authorization_token(request):
    header = get_authorization_header(request).decode()
    try:
        tape, token = header.split()
        if tape.lower() != 'bearer':
            return None
        return token
    except ValueError:
        return None


class TokenMiddleware(SessionMiddleware):
    def process_request(self, request):
        request.raw_token = get_authorization_token(request)
        try:
            session_key = AccessToken(request.raw_token, verify=False)[settings.SESSION_COOKIE_NAME]
        except:
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        request.session = self.SessionStore(session_key)


class NonceMiddleware(MiddlewareMixin):
    def get_nonce(self, request):
        nonce = request.META.get('HTTP_NONCE', b'')
        if isinstance(nonce, str):
            nonce = nonce.encode()
        return nonce

    def process_request(self, request):
        conn = get_redis_connection()
        raw_nonce = self.get_nonce(request)
        timestamp, nonce, signature = raw_nonce.decode().split('.')
        secret_key = request.session['_']
        # 验证签名
        if hmac.new(force_bytes(secret_key), raw_nonce, 'md5').hexdigest() != signature:
            return JsonResponse({'nonce': 'signature failed'})

        # 验证时间戳
        current_time = make_timestamp(aware_utcnow())
        if not (0 <= current_time - int(timestamp) <= 60):
            return JsonResponse({'nonce': 'timestamp failed'})

        # 验证唯一值
        if conn.sismember('nonce', nonce):
            return JsonResponse({'nonce': 'nonce exist'})

        conn.sadd('nonce', nonce)

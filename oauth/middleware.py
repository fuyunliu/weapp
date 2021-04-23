from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware

from oauth import get_authorization_token
from oauth.backends import token_backend


class TokenMiddleware(SessionMiddleware):

    def process_request(self, request):
        request.raw_token = get_authorization_token(request)
        try:
            session_key = token_backend.get_unverified_payload(request.raw_token)[settings.SESSION_COOKIE_NAME]
        except:
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        request.session = self.SessionStore(session_key)

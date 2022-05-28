from uuid import uuid4
from datetime import timedelta

from django.conf import settings
from commons.utils import aware_utcnow, make_timestamp, from_timestamp


class Token:
    """
    https://github.com/jazzband/djangorestframework-simplejwt
    """
    token_type = None
    lifetime = None

    def __init__(self, raw_token=None, verify=True, leeway=0):
        assert self.token_type is not None, 'Cannot create token with no type.'
        assert self.lifetime is not None, 'Cannot create token with no lifetime.'

        self.raw_token = raw_token
        self.current_time = aware_utcnow()

        if raw_token is not None:
            # decode the given token
            from oauth.backends import token_backend
            self.payload = token_backend.decode(raw_token, verify=verify, leeway=leeway)
            _ = self.verify(leeway=leeway) if verify else None
        else:
            # create a new token
            self.payload = {}
            self.set_jti()
            self.set_jtp()
            self.set_iat()
            self.set_exp()

    def __repr__(self):
        return repr(self.payload)

    def __getitem__(self, key):
        return self.payload[key]

    def __setitem__(self, key, value):
        self.payload[key] = value

    def __delitem__(self, key):
        del self.payload[key]

    def __contains__(self, key):
        return key in self.payload

    def __str__(self):
        from oauth.backends import token_backend
        return token_backend.encode(self.payload)

    def verify(self, leeway=0):
        self.check_jti()
        self.check_jtp()
        self.check_iat()
        self.check_exp(leeway=leeway)

    def set_jti(self, claim='jti'):
        self.payload[claim] = uuid4().hex

    def set_jtp(self, claim='jtp'):
        self.payload[claim] = self.token_type

    def set_iat(self, claim='iat', from_time=None):
        from_time = from_time or self.current_time
        self.payload[claim] = make_timestamp(from_time)

    def set_exp(self, claim='exp', from_time=None, lifetime=None):
        from_time = from_time or self.current_time
        lifetime = lifetime or self.lifetime
        self.payload[claim] = make_timestamp(from_time + lifetime)

    def check_jti(self, claim='jti'):
        jti = self.payload.get(claim)
        assert jti is not None, f"Token has no '{claim}' claim."

    def check_jtp(self, claim='jtp'):
        jtp = self.payload.get(claim)
        assert jtp is not None, f"Token has no '{claim}' claim."
        assert jtp == self.token_type, 'Token has wrong type.'

    def check_iat(self, claim='iat'):
        iat = self.payload.get(claim)
        assert iat is not None, f"Token has no '{claim}' claim."

    def check_exp(self, claim='exp', current_time=None, leeway=0):
        current_time = current_time or self.current_time
        leeway = leeway.total_seconds() if isinstance(leeway, timedelta) else leeway
        exp = self.payload.get(claim)
        assert exp is not None, f"Token has no '{claim}' claim."
        expire_time = from_timestamp(exp + leeway)
        assert expire_time > current_time, f"Token '{claim}' claim has expired."

    @classmethod
    def for_user(cls, user):
        user_id = getattr(user, settings.OAUTH['USER_ID_FIELD'])
        user_id = user_id if isinstance(user_id, int) else str(user_id)

        token = cls()
        token[settings.OAUTH['USER_ID_CLAIM']] = user_id

        return token


class AccessToken(Token):
    token_type = 'access'
    lifetime = settings.OAUTH['ACCESS_TOKEN_LIFETIME']

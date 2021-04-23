from uuid import uuid4
from datetime import timedelta

from django.conf import settings
from commons.utils import aware_utcnow, make_timestamp, from_timestamp


class Token:
    token_type = None
    lifetime = None
    type_claim = 'token_type'

    def __init__(self, token=None, verify=True, leeway=0):
        assert (self.token_type is not None or self.lifetime is not None), \
            'Cannot create token with no type or lifetime'

        self.token = token
        self.current_time = aware_utcnow()

        if token is not None:
            # decode the given token
            from oauth.backends import token_backend
            self.payload = token_backend.decode(token, verify=verify, leeway=leeway)
            _ = self.verify() if verify else None
        else:
            # create a new token
            self.payload = {self.type_claim: self.token_type}
            self.set_exp(from_time=self.current_time, lifetime=self.lifetime)
            self.set_jti()

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

    def get(self, key, default=None):
        return self.payload.get(key, default)

    def __str__(self):
        from oauth.backends import token_backend
        return token_backend.encode(self.payload)

    def verify(self):
        self.check_exp()
        assert 'jti' in self.payload, 'Token has no id.'
        self.verify_token_type()

    def verify_token_type(self):
        token_type = self.get(self.type_claim)
        assert token_type is not None, 'Token has no type.'
        assert self.token_type == token_type, 'Token has wrong type.'

    def set_jti(self):
        self.payload['jti'] = uuid4().hex

    def set_exp(self, from_time=None, lifetime=None):
        from_time = from_time or self.current_time
        lifetime = lifetime or self.lifetime
        self.payload['iat'] = make_timestamp(from_time)
        self.payload['exp'] = make_timestamp(from_time + lifetime)

    def check_exp(self, current_time=None):
        current_time = current_time or self.current_time
        claim_value = self.get('exp')
        assert claim_value is not None, "Token has no 'exp' claim."
        claim_time = from_timestamp(claim_value)
        assert claim_time > current_time, "Token 'exp' claim has expired."

    @classmethod
    def for_user(cls, user):
        user_id = getattr(user, getattr(settings, 'USER_ID_FIELD', 'id'))
        user_id = user_id if isinstance(user_id, int) else str(user_id)

        token = cls()
        token[getattr(settings, 'USER_ID_CLAIM', 'user_id')] = user_id

        return token


class AccessToken(Token):
    token_type = 'access'
    lifetime = settings.ACCESS_TOKEN_LIFETIME


class UntypedToken(Token):
    token_type = 'untyped'
    lifetime = timedelta(seconds=0)

    def verify_token_type(self):
        pass

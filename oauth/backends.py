import jwt
from django.conf import settings
from jwt import algorithms

from commons.constants import Messages


class TokenBackend:
    ALLOWED_ALGORITHMS = ('HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512')

    def __init__(
        self,
        algorithm,
        signing_key=None,
        verifying_key=None,
        audience=None,
        issuer=None,
    ):
        self.algorithm = self._validate_algorithm(algorithm)
        self.verifying_key = signing_key if algorithm.startswith('HS') else verifying_key
        self.signing_key = signing_key
        self.audience = audience
        self.issuer = issuer

    def _validate_algorithm(self, algorithm):
        assert algorithm in self.ALLOWED_ALGORITHMS, Messages.UNKNOWN_ALGORITHM.format(algorithm)

        if algorithm in algorithms.requires_cryptography:
            assert algorithms.has_crypto, Messages.REQUIRE_CRYPTO.format(algorithm)

        return algorithm

    def encode(self, payload, headers=None):
        data = payload.copy()
        if self.audience is not None:
            data['aud'] = self.audience
        if self.issuer is not None:
            data['iss'] = self.issuer
        token = jwt.encode(data, self.signing_key, algorithm=self.algorithm, headers=headers)
        return token

    def decode(self, token, verify=True, leeway=0):
        return jwt.decode(
            token,
            self.verifying_key,
            algorithms=[self.algorithm],
            verify=verify,
            audience=self.audience,
            issuer=self.issuer,
            leeway=leeway,
            options={
                'verify_aud': self.audience is not None,
                'verify_iss': self.issuer is not None,
                'verify_iat': verify,
                'verify_signature': verify
            }
        )


token_backend = TokenBackend(
    'HS256',
    signing_key=settings.SECRET_KEY,
    verifying_key=None,
    audience=None,
    issuer=None
)

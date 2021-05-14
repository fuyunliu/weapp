class Messages:
    TOKEN_NOT_FOUND = 'Token id does not exist within session.'
    TOKEN_MISMATCH = 'Token id mismatch within session.'
    UNKNOWN_UID = 'Token contained no recognizable user identification.'
    UNKNOWN_ALGORITHM = "Unrecognized algorithm '{0}'"
    REQUIRE_CRYPTO = "You must have cryptography installed to use '{0}'"
    USER_NOT_FOUND = 'User object does not exist.'
    USER_INACTIVE = 'User object is inactive.'
    EMAIL_OR_PHONE = 'Email or Phone are required.'
    PASSWORD_MISMATCH = "The two password fields didn't match."
    WRONG_PHONE_CODE = 'Phone Code authenticate failed.'
    WRONG_PASSWORD = 'Password authenticate failed.'
    NEW_USERNAME = 'You can set your username after {0} days.'
    NEW_NICKNAME = 'You can set your nickname after {0} days.'
    USERNAME_EXIST = 'Username already exists.'
    NICKNAME_EXIST = 'Nickname already exists.'
    EMAIL_EXIST = 'Email already exists.'
    PHONE_EXIST = 'Phone already exists'
    OBJECT_NOT_FOUND = 'Object does not exist.'
    CT_NOT_ALLOWED = 'Not allowed content type.'


class CacheKeySet:
    PHONE_CODE = 'oauth:{field}:{value}:{tape}.code'

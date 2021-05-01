class Messages:
    TOKEN_NOT_EXIST = 'Token id does not exist.'
    TOKEN_MISMATCH = 'Token id mismatch.'
    UNKNOWN_UID = 'Token contained no recognizable user identification.'
    UNKNOWN_ALGORITHM = "Unrecognized algorithm '{0}'"
    REQUIRE_CRYPTO = "You must have cryptography installed to use '{0}'"
    USER_NOT_EXIST = 'User object does not exist.'
    USER_INACTIVE = 'User object is inactive.'
    EMAIL_PHONE = 'Email or Phone are required.'
    PASSWORD_MISMATCH = "The two password fields didn't match."
    WRONG_DIGITS = 'Wrong digits.'
    WRONG_PASSWORD = 'Wrong password.'
    NEW_USERNAME = 'You can set your username after {0} days.'
    NEW_NICKNAME = 'You can set your nickname after {0} days.'
    USERNAME_EXIST = 'Username already exists.'
    NICKNAME_EXIST = 'Nickname already exists.'
    EMAIL_EXIST = 'Email already exists.'
    PHONE_EXIST = 'Phone already exists'


class CacheKeySet:
    EMAIL_DIGITS = 'oauth:email:{email}:{tape}.digits'
    PHONE_DIGITS = 'oauth:phone:{phone}:{tape}.digits'

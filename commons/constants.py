class Messages:
    TOKEN_NOT_EXIST = 'Token id does not exist.'
    TOKEN_MISMATCH = 'Token id mismatch.'
    UID_KEYERROR = 'Token contained no recognizable user identification.'
    USER_NOT_EXIST = 'User object does not exist.'
    USER_INACTIVE = 'User object is inactive.'
    EMAIL_PHONE = 'Email or Phone are required.'
    WRONG_DIGITS = 'Wrong digits.'
    WRONG_PASSWORD = 'Wrong password.'


class CacheKey:
    EMAIL_DIGITS = 'oauth:email:{email}.digits'
    PHONE_DIGITS = 'oauth:phone:{phone}.digits'

import itertools
import re
import secrets
import string
import time
from calendar import timegm
from datetime import datetime

import pendulum
from django.conf import settings
from django.utils.timezone import is_naive, make_aware, utc

from commons import hanzi

random = secrets.SystemRandom()


def get_random_string(length=12, chars=string.ascii_letters+string.digits):
    return ''.join(random.choice(chars) for _ in range(length))


def get_random_secret():
    chars = string.ascii_lowercase + string.digits + '!@#$%^&*(-_=+)'
    return get_random_string(50, chars)


def get_random_number():
    chars = string.digits
    return get_random_string(6, chars)


def get_random_name():
    chars = string.ascii_lowercase + string.digits
    namespace = settings.OAUTH['USERNAME_RANDOM_NAMESPACE']
    name = '_'.join((namespace, get_random_string(14, chars)))
    return name


def make_nonce():
    return str(time.time()) + str(random.randint(0, 999999))


def chunks(iterable, size):
    it = iter(iterable)
    while item := list(itertools.islice(it, size)):
        yield item


def timesince(dt):
    return pendulum.instance(dt).diff_for_humans()


def make_utc(dt):
    if settings.USE_TZ and is_naive(dt):
        return make_aware(dt, timezone=utc)
    return dt


def aware_utcnow():
    return make_utc(datetime.utcnow())


def make_timestamp(dt):
    return timegm(dt.utctimetuple())


def from_timestamp(ts):
    return make_utc(datetime.utcfromtimestamp(ts))


def string_split(text):
    text = text.strip()
    if not text:
        return []
    return re.split(r'[;,\s]\s*', text)


def is_lower_alphabet(char):
    """小写字母"""
    return '\u0061' <= char <= '\u007A'


def is_upper_alphabet(char):
    """大写字母"""
    return '\u0041' <= char <= '\u005A'


def is_alphabet(char):
    """英文字母"""
    return is_lower_alphabet(char) or is_upper_alphabet(char)


def is_whitespace(char):
    """空白符"""
    return char in string.whitespace


def is_empty_string(char):
    """空字符串"""
    return not char


def is_en_punctuation(char):
    """英文标点"""
    return char in string.punctuation


def is_cn_punctuation(char):
    """中文标点"""
    return char in hanzi.punctuation


def is_chinese(char):
    """中文"""
    return '\u4e00' <= char <= '\u9fff'


def is_hyphen(char):
    """
    常见连字符: <>._-/
    为了保持标签名称的干净整洁，只允许使用 `-` 作为连字符
    """
    return char in '-'


def is_en_number(char):
    """英文数字"""
    return '\u0030' <= char <= '\u0039'


def is_cn_number(char):
    """中文数字"""
    return char in hanzi.numbers


def is_basic_latin_control(char):
    return char in hanzi.basic_latin_control_characters


def is_separator(char):
    return (
        is_en_punctuation(char) or
        is_cn_punctuation(char) or
        is_whitespace(char) or
        is_basic_latin_control(char)
    )


def word_tokenize(text):
    """中英文分词"""
    chars = []
    for char in text:
        if is_separator(char) and not is_hyphen(char):
            if chars:
                if not all(map(is_hyphen, chars)):
                    yield ''.join(chars)
                chars = []
        else:
            chars.append(char)

    if chars:
        yield ''.join(chars)

import itertools
import secrets
import string
from calendar import timegm
from datetime import datetime

import pendulum
from django.conf import settings
from django.utils.timezone import is_naive, make_aware, utc

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
    namespace = getattr(settings, 'USERNAME_RANDOM_NAMESPACE', 'uid')
    name = '_'.join((namespace, get_random_string(14, chars)))
    return name


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

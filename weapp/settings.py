from datetime import timedelta
from weapp.config import config

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config['DEBUG']

ALLOWED_HOSTS = []

INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'channels',

    'debug_toolbar',
    'drf_spectacular',

    'oauth.apps.OAuthConfig',
    'weblog.apps.WeblogConfig',
    'collects.apps.CollectsConfig',
    'comments.apps.CommentsConfig',
    'follows.apps.FollowsConfig',
    'likes.apps.LikesConfig',
    'taggit.apps.TaggitConfig',
    'polls.apps.PollsConfig',
    'poetry.apps.PoetryConfig',
    'wechat.apps.WechatConfig',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'oauth.middleware.TokenMiddleware',  # Wrapped SessionMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'weapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'weapp.wsgi.application'

# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = config['DATABASES']

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/oauth/login/'

LOGIN_REDIRECT_URL = '/oauth/'

LOGOUT_REDIRECT_URL = LOGIN_URL

# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'

AUTH_USER_MODEL = 'oauth.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        # 'oauth.authentication.TokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'HTML_SELECT_CUTOFF': 10,
    'PAGE_SIZE': 10,
}

USERNAME_RANDOM_NAMESPACE = 'uid'
PHONENUMBER_DEFAULT_REGION = 'CN'
USERNAME_MODIFY_TIMEDELTA = timedelta(days=365)
NICKNAME_MODIFY_TIMEDELTA = timedelta(days=90)
USER_DESTROY_TIMEDELTA = timedelta(days=14)

# https://github.com/SimpleJWT/django-rest-framework-simplejwt#settings
ACCESS_TOKEN_LIFETIME = timedelta(minutes=10)
CAPTCHA_LIFETIME = timedelta(minutes=10)
USER_ID_FIELD = 'id'
USER_ID_CLAIM = 'user_id'

# https://docs.djangoproject.com/en/3.2/topics/logging/
# LOGGING = {
#     'version': 1,
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue'
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler'
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console']
#         }
#     }
# }

# https://docs.djangoproject.com/zh-hans/3.2/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LIKE_MODELS = {
    "weblog.article": {
        # 'serializer': 'weblog.serializers.ArticleSerializer'
    },
    "weblog.pin": {
        # 'serializer': 'weblog.serializers.PinSerializer'
    }
}

ASGI_APPLICATION = 'weapp.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)]
        }
    }
}

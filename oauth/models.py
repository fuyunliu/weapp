from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.functional import cached_property
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.db.models.manager import EmptyManager

from commons.fields.models import PhoneField
from commons.utils import get_random_name


def _username_mtime():
    return timezone.now() - settings.USERNAME_MODIFY_TIMEDELTA


def _nickname_mtime():
    return timezone.now() - settings.NICKNAME_MODIFY_TIMEDELTA


class User(AbstractUser):
    phone = PhoneField('手机号码', blank=True)
    # stars=我关注的人 fans=关注我的人
    # stars = models.ManyToManyField(
    #     'self',
    #     related_name='fans',
    #     symmetrical=False, # 非对称关系
    #     verbose_name='我关注的人'
    # )
    name_mtime = models.DateTimeField('用户名修改时间', default=_username_mtime, editable=False)

    class Meta(AbstractUser.Meta):
        ordering = ['-id']
        get_latest_by = 'id'

    def save(self, *args, **kwargs):
        if not self.username:
            self.set_username()
        super().save(*args, **kwargs)

    def set_username(self, username=None):
        while True:
            username = username or get_random_name()
            obj = self.__class__.objects.filter(username=username).first()
            if obj is None or obj == self:
                break
            username = None
        self.username = self.normalize_username(username)
        self.name_mtime = timezone.now()


class Profile(models.Model):
    class Gender(models.IntegerChoices):
        MALE = 0, 'Male'
        FEMALE = 1, 'Female'

        __empty__ = 'Unknown'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )
    nickname = models.CharField('昵称', max_length=64, unique=True)
    gender = models.IntegerField('性别', null=True, choices=Gender.choices)
    birthday = models.DateField('生日', null=True, blank=True)
    location = models.CharField('地区', max_length=64, blank=True)
    about_me = models.TextField('签名', blank=True)
    avatar_hash = models.CharField('头像哈希值', max_length=32)
    nick_mtime = models.DateTimeField('昵称修改时间', default=_nickname_mtime, editable=False)

    class Meta:
        ordering = ['-user_id']
        verbose_name = '个人资料'
        verbose_name_plural = verbose_name
        get_latest_by = 'user_id'

    def __str__(self):
        return f'<Profile {self.nickname}>'

    def save(self, *args, **kwargs):
        if not self.nickname:
            self.set_nickname()
        super().save(*args, **kwargs)

    def set_nickname(self, nickname=None):
        self.nickname = nickname or self.user.username
        self.nick_mtime = timezone.now()


def create_profile(sender, **kwargs):
    if kwargs['created']:
        profile = Profile()
        profile.user = kwargs['instance']
        profile.save()
post_save.connect(create_profile, sender=User)


class Region(models.Model):
    class Level(models.IntegerChoices):
        PROVINCCE = 1, 'Province'
        CITY = 2, 'City'
        COUNTRY = 3, 'Country'
        TOWN = 4, 'Town'
        VILLAGE = 5, 'Village'

    name = models.CharField('名称', max_length=32)
    code = models.CharField('代码', max_length=32)
    level = models.IntegerField('级别', choices=Level.choices)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='上级地区',
        null=True
    )

    class Meta:
        verbose_name = '行政区划'
        verbose_name_plural = verbose_name


class TokenUser:
    """
    Instances of this class act as stateless user objects which are backed by validated tokens.
    """
    is_active = True

    _groups = EmptyManager(Group)
    _user_permissions = EmptyManager(Permission)

    def __init__(self, token):
        self.token = token

    def __str__(self):
        return f'TokenUser {self.id}'

    @cached_property
    def id(self):
        return self.token[settings.USER_ID_CLAIM]

    @cached_property
    def pk(self):
        return self.id

    @cached_property
    def username(self):
        return self.token.get('username', '')

    @cached_property
    def is_staff(self):
        return self.token.get('is_staff', False)

    @cached_property
    def is_superuser(self):
        return self.token.get('is_superuser', False)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def save(self):
        raise NotImplementedError('Token users have no DB representation.')

    def delete(self):
        raise NotImplementedError('Token users have no DB representation.')

    def set_password(self, raw_password):
        raise NotImplementedError('Token users have no DB representation.')

    def check_password(self, raw_password):
        raise NotImplementedError('Token users have no DB representation.')

    @property
    def groups(self):
        return self._groups

    @property
    def user_permissions(self):
        return self._user_permissions

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return set()

    def has_perm(self, perm, obj=None):
        return False

    def has_perms(self, perm_list, obj=None):
        return False

    def has_module_perms(self, module):
        return False

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def get_username(self):
        return self.username

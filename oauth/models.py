from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission, UserManager
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.manager import EmptyManager
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.functional import cached_property

from commons.fields.models import PhoneField
from commons.managers import GenericQuerySet, ManagerDescriptor, GenericRelatedManager, GenericReversedManager
from commons.utils import get_random_name


def _username_mtime():
    return timezone.now() - settings.USERNAME_MODIFY_TIMEDELTA


def _nickname_mtime():
    return timezone.now() - settings.NICKNAME_MODIFY_TIMEDELTA


class User(AbstractUser):
    phone = PhoneField('手机号码', blank=True)
    # stars=关注 fans=粉丝
    # stars = models.ManyToManyField(
    #     'self',
    #     related_name='fans',
    #     symmetrical=False, # 非对称关系
    #     verbose_name='关注'
    # )
    name_mtime = models.DateTimeField('改名时间', default=_username_mtime, editable=False)

    objects = UserManager.from_queryset(GenericQuerySet)()

    # 我关注的人
    following = ManagerDescriptor(manager=GenericRelatedManager, through='follows.Follow', target='oauth.User')

    # 关注我的人
    followers = ManagerDescriptor(manager=GenericReversedManager, through='follows.Follow', target='oauth.User')

    # 我喜欢的收藏夹
    liking_collections = ManagerDescriptor(manager=GenericRelatedManager, through='likes.Like', target='collects.Collection')

    # 我关注的收藏夹
    following_collections = ManagerDescriptor(manager=GenericRelatedManager, through='follows.Follow', target='collects.Collection')

    # 我喜欢的评论
    liking_comments = ManagerDescriptor(manager=GenericRelatedManager, through='likes.Like', target='comments.Comment')

    # 我喜欢的文章
    liking_articles = ManagerDescriptor(manager=GenericRelatedManager, through='likes.Like', target='weblog.Article')

    # 我喜欢的想法
    liking_pins = ManagerDescriptor(manager=GenericRelatedManager, through='likes.Like', target='weblog.Pin')

    # 我关注的分类
    following_categories = ManagerDescriptor(manager=GenericRelatedManager, through='follows.Follow', target='weblog.Category')

    # 我关注的话题
    following_topics = ManagerDescriptor(manager=GenericRelatedManager, through='follows.Follow', target='weblog.Topic')

    class Meta(AbstractUser.Meta):
        ordering = ['id']
        get_latest_by = 'id'

    def save(self, *args, **kwargs):
        if not self.username:
            self.set_username()
        super().save(*args, **kwargs)

    def set_username(self, username=None):
        def names():
            if username:
                yield username
            if self.username:
                yield self.username
            while True:
                yield get_random_name()

        normalize_username = self.normalize_username
        for name in names():
            name = normalize_username(name)
            obj = self.__class__.objects.filter(username=name).first()
            if obj is None or obj == self:
                self.username = name
                self.name_mtime = timezone.now()
                break


class Profile(models.Model):
    class Gender(models.IntegerChoices):
        MALE = 0, '男'
        FEMALE = 1, '女'

        __empty__ = '保密'

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
    nick_mtime = models.DateTimeField('改名时间', default=_nickname_mtime, editable=False)

    class Meta:
        ordering = ['user_id']
        verbose_name = '个人资料'
        verbose_name_plural = verbose_name
        get_latest_by = 'user_id'

    def __str__(self):
        return self.nickname

    def is_owned(self, user):
        return self.user == user

    def save(self, *args, **kwargs):
        if not self.nickname:
            self.set_nickname()
        super().save(*args, **kwargs)

    def set_nickname(self, nickname=None):
        def names():
            if nickname:
                yield nickname
            if self.nickname:
                yield self.nickname
            yield self.user.username
            while True:
                yield get_random_name()

        normalize_nickname = self.user.normalize_username
        for name in names():
            name = normalize_nickname(name)
            obj = self.__class__.objects.filter(nickname=name).first()
            if obj is None or obj == self:
                self.nickname = name
                self.nick_mtime = timezone.now()
                break


def create_profile(sender, **kwargs):
    if kwargs['created']:
        profile = Profile()
        profile.user = kwargs['instance']
        profile.save()


post_save.connect(create_profile, sender=User)


class Region(models.Model):
    class Level(models.IntegerChoices):
        PROVINCE = 1, '省'
        CITY = 2, '市'
        COUNTRY = 3, '县'
        TOWN = 4, '镇'
        VILLAGE = 5, '村'

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

    def __str__(self):
        return self.name


class TokenUser:
    """
    Instances of this class act as stateless user objects which are backed by validated tokens.
    """
    is_active = True

    _groups = EmptyManager(Group)
    _user_permissions = EmptyManager(Permission)

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self}>'

    def __str__(self):
        return self.pk

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

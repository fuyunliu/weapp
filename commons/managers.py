import functools

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.aggregates import Count, Max, Min
from django.db.models.fields.related import ForeignObject
from django.db.models.manager import Manager
from django.db.models.options import Options
from django.db.models.query import QuerySet
from django.db.models.sql import AND
from django.db.models.sql.datastructures import Join
from django.db.models.sql.where import WhereNode

from commons.utils import random


class GenericQuerySet(QuerySet):

    def random(self, amount=1):
        with transaction.atomic(using=self.db):
            q = self.aggregate(min_id=Min('id'), max_id=Max('id'), count=Count('id'))
            if q['count'] == 0:
                return self.none()
            if q['count'] <= amount:
                return self.all()
            max_id = self.order_by('-pk')[amount:amount+1].first().pk
            pk = random.randint(q['min_id'], max_id)
            return self.order_by('pk').filter(pk__gt=pk)[:amount]


class ManagerDescriptor:

    def __init__(self, manager, **kwargs):
        self.manager = manager
        self.kwargs = kwargs

    def __get__(self, instance, model):
        if instance is None:
            raise AttributeError(f"Manager isn't accessible via {model.__name__}.")

        if instance.pk is None:
            raise AttributeError(f"Manager isn't accessible via {model.__name__} instance with no primary key.")

        return self.manager(instance=instance, model=model, **self.kwargs)


class GenericRelatedManager(Manager):
    """
    动作的执行者使用这个类
        - 我关注的人
        - 我关注的收藏夹
        - 我关注的分类
        - 我关注的话题
        - 我喜欢的收藏夹
        - 我喜欢的评论
        - 我喜欢的文章
        - 我喜欢的动态
        - 收藏夹收藏的文章
        - 收藏夹收藏的动态

    """

    def __init__(self, instance, model, through, target) -> None:
        """
        Args:
            instance (Model instance): 实例对象
            model (instance Model): 实例模型
            through (through Model): 中间模型
            target (target Model): 目标模型
        """
        super().__init__()
        self.model = model
        self.instance = instance
        self.through = apps.get_model(through)
        self.target = apps.get_model(target)

    def get_queryset(self):
        md_pk, ct_pk = None, None
        for field in self.through._meta.fields:
            if field.related_model is self.model:
                md_pk = field.column
            if field.related_model is ContentType:
                ct_pk = field.column

        assert (md_pk is not None and ct_pk is not None)
        tg_pk = self.through._meta.private_fields[0].fk_field

        kwargs = {md_pk: self.instance.pk, ct_pk: ContentType.objects.get_for_model(self.target).pk}
        queryset = self.target._default_manager.filter(pk__in=self.through._default_manager.filter(**kwargs).values(tg_pk))

        return queryset


class GenericReversedManager(Manager):
    """
    动作的接受者使用这个类
        - 贴给我的标签
        - 关注我的人
        - 喜欢收藏夹的人
        - 关注收藏夹的人
        - 喜欢评论的人
        - 喜欢文章的人
        - 收藏文章的收藏夹
        - 喜欢动态的人
        - 收藏动态的收藏夹
        - 关注分类的人
        - 关注话题的人

    """

    def __init__(self, instance, model, through, target) -> None:
        """
        Args:
            instance (Model instance): 实例对象
            model (instance Model): 实例模型
            through (through Model): 中间模型
            target (target Model): 目标模型
        """
        super().__init__()
        self.model = model
        self.instance = instance
        self.through = apps.get_model(through)
        self.target = apps.get_model(target)

    def get_queryset(self):
        tg_pk, ct_pk = None, None
        for field in self.through._meta.fields:
            if field.related_model is self.target:
                tg_pk = field.column
            if field.related_model is ContentType:
                ct_pk = field.column

        assert (tg_pk is not None and ct_pk is not None)
        md_pk = self.through._meta.private_fields[0].fk_field

        kwargs = {md_pk: self.instance.pk, ct_pk: ContentType.objects.get_for_model(self.model).pk}
        queryset = self.target._default_manager.filter(pk__in=self.through._default_manager.filter(**kwargs).values(tg_pk))

        return queryset


class GenericJoin(Join):
    """
    BUG: QuerySet must filter something or else it will cause SQL Error.

    Sample:
    ```python
        # left = Article right = Like
        q = Article.objects.filter(status=1)
        join = GenericJoin(Article, Like, LOUTER, (('id', 'object_id'),), (('content_type', 10), ('sender', 2)))
        q.query.join(join)
    ```
    """

    def __init__(self, left, right, join_type, join_cols, extra_conds=None):
        """
        Args:
            left (Model): 左表
            right (Model): 右表
            join_type (str): 连接类型
            join_cols (tuple): 连接字段
            extra_conds (tuple): 额外连接条件
        """
        def get_joining_columns():
            return tuple((left_field, right_field) for left_field, right_field in join_cols)

        join_field = ForeignObject(
            to=right,
            on_delete=lambda: None,
            from_fields=[None],
            to_fields=[None]
        )
        join_field.opts = Options(left._meta)
        join_field.opts.model = left
        join_field.get_joining_columns = get_joining_columns
        super().__init__(right._meta.db_table, left._meta.db_table, 'T', join_type, join_field, True)

        def get_extra_restriction(self, left, right, extra_conds):
            if extra_conds is None:
                return None

            def get_lookup(fname, fvalue):
                field = right._meta.get_field(fname)
                lookup = field.get_lookup('exact')(field.get_col(self.table_alias), fvalue)
                return lookup

            return WhereNode([get_lookup(fname, fvalue) for fname, fvalue in extra_conds], connector=AND)

        self.get_extra_restriction = functools.partial(get_extra_restriction, self=self, left=left, right=right, extra_conds=extra_conds)

    def as_sql(self, compiler, connection):
        join_conditions = []
        params = []
        qn = compiler.quote_name_unless_alias
        qn2 = connection.ops.quote_name

        # Add a join condition for each pair of joining columns.
        for lhs_col, rhs_col in self.join_cols:
            join_conditions.append('%s.%s = %s.%s' % (
                qn(self.parent_alias),
                qn2(lhs_col),
                qn(self.table_alias),
                qn2(rhs_col),
            ))

        # Add a single condition inside parentheses for whatever
        # get_extra_restriction() returns.
        extra_cond = self.join_field.get_extra_restriction(self.table_alias, self.parent_alias)
        if extra_cond:
            extra_sql, extra_params = compiler.compile(extra_cond)
            join_conditions.append('(%s)' % extra_sql)
            params.extend(extra_params)

        # 添加额外的 Join On 条件
        extra_cond = self.get_extra_restriction()
        if extra_cond:
            extra_sql, extra_params = compiler.compile(extra_cond)
            join_conditions.append('(%s)' % extra_sql)
            params.extend(extra_params)

        if self.filtered_relation:
            extra_sql, extra_params = compiler.compile(self.filtered_relation)
            if extra_sql:
                join_conditions.append('(%s)' % extra_sql)
                params.extend(extra_params)
        if not join_conditions:
            # This might be a rel on the other end of an actual declared field.
            declared_field = getattr(self.join_field, 'field', self.join_field)
            raise ValueError(
                "Join generated an empty ON clause. %s did not yield either "
                "joining columns or extra restrictions." % declared_field.__class__
            )
        on_clause_sql = ' AND '.join(join_conditions)
        alias_str = '' if self.table_alias == self.table_name else (' %s' % self.table_alias)
        sql = '%s %s%s ON (%s)' % (self.join_type, qn(self.table_name), alias_str, on_clause_sql)
        return sql, params

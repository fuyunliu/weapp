import random
from django.apps import apps
from django.db import models, transaction
from django.db.models import Count, Max, Min
from django.contrib.contenttypes.models import ContentType


class GenericQuerySet(models.QuerySet):

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


class GenericRelatedManager(models.Manager):
    """
    动作的发出者使用这个类
    """

    def __init__(self, instance, model, through, target):
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


class GenericReversedManager(models.Manager):
    """
    动作的接受者使用这个类
    """

    def __init__(self, instance, model, through, target):
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

import random
from django.db import models, transaction
from django.db.models import Count, Max, Min


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


class GenericManager(models.Manager):

    def random(self, *args, **kwargs):
        return self.get_queryset().random(*args, **kwargs)

    def get_queryset(self):
        return GenericQuerySet(self.model, using=self._db)

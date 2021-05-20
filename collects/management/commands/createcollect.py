from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from weblog.models import Article, Pin
from collects.models import Collect, Collection
from faker import Faker


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='+', type=int)

    def handle(self, *args, **options):
        count = options['count'][0]
        user_model = get_user_model()
        faker = Faker()

        for _ in range(int(count)):
            fields = {'name': faker.word(), 'desc': faker.text()}
            try:
                collection = Collection(**fields)
                collection.owner = user_model.objects.random().first()
                collection.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create collection {collection.pk}'))

        for _ in range(int(count)):
            try:
                collect = Collect()
                collect.collection = Collection.objects.random().first()
                collect.content_object = Article.objects.random().first()
                collect.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create collect {collect.pk}'))

        for _ in range(int(count)):
            try:
                collect = Collect()
                collect.collection = Collection.objects.random().first()
                collect.content_object = Pin.objects.random().first()
                collect.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create collect {collect.pk}'))

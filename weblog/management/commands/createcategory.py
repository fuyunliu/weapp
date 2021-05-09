from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from weblog.models import Category
from faker import Faker


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='+', type=int)

    def handle(self, *args, **options):
        count = options['count'][0]
        faker = Faker()
        for _ in range(int(count)):
            fields = {
                'name': faker.word()
            }
            try:
                cate = Category.objects.create(**fields)
                cate.save()
            except IntegrityError:
                self.stdout.write(self.style.ERROR('创建失败！'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create category {cate.name}'))

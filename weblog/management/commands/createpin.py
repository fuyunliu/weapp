from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from weblog.models import Pin
from faker import Faker


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='+', type=int)

    def handle(self, *args, **options):
        count = options['count'][0]
        faker = Faker()
        user_model = get_user_model()
        for _ in range(int(count)):
            fields = {
                'body': faker.text()
            }
            try:
                pin = Pin(**fields)
                pin.author = user_model.objects.random().first()
                pin.save()
            except IntegrityError:
                self.stdout.write(self.style.ERROR('创建失败！'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create pin {pin.pk}'))

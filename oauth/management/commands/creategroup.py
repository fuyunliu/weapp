from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db.utils import IntegrityError
from faker import Faker


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='+', type=int)

    def handle(self, *args, **options):
        count = options['count'][0]
        faker = Faker()
        for _ in range(int(count)):
            fields = {'name': faker.word()}
            try:
                group = Group.objects.create(**fields)
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create user {group.name}'))

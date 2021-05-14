from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone
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
                'username': faker.user_name(),
                'email': faker.email(),
                'phone': faker.phone_number(),
                'password': '123456qw',
                'first_name': faker.first_name(),
                'last_name': faker.last_name(),
                'date_joined': timezone.now(),
                'last_login': timezone.now()
            }
            try:
                user = user_model.objects.create_user(**fields)
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create user {user.username}'))

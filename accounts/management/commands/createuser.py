from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from faker import Faker


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='+', type=int)

    def handle(self, *args, **options):
        count = options['count'][0]
        faker = Faker()
        password = make_password('123456qw')
        user_model = get_user_model()
        for _ in range(int(count)):
            user = {
                'username': faker.user_name(),
                'email': faker.email(),
                'password': password,
                'nickname': faker.name(),
                'location': faker.city(),
                'about_me': faker.text(),
                'date_joined': timezone.now()
            }
            try:
                user_model.objects.create(**user)
                user_model.save()
            except:
                CommandError('创建失败！')
            self.stdout.write(self.style.SUCCESS(f'Successfully create user {user["username"]}'))

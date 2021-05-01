from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from weblog.models import Topic
from faker import Faker


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='+', type=int)

    def handle(self, *args, **options):
        count = options['count'][0]
        faker = Faker()
        for _ in range(int(count)):
            fields = {
                'name': faker.name()
            }
            try:
                topic = Topic.objects.create(**fields)
                topic.save()
            except IntegrityError:
                CommandError('创建失败！')
            self.stdout.write(self.style.SUCCESS(f'Successfully create topic {fields["name"]}'))

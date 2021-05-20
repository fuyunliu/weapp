from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from polls.models import Question
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
                'title': faker.sentence(),
                'max_choices': 1,
            }
            try:
                question = Question(**fields)
                question.owner = user_model.objects.random().first()
                question.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create question {question.pk}'))

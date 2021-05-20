from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from polls.models import Choice, Vote


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='+', type=int)

    def handle(self, *args, **options):
        count = options['count'][0]
        user_model = get_user_model()
        for _ in range(int(count)):
            try:
                vote = Vote()
                vote.user = user_model.objects.random().first()
                vote.choice = Choice.objects.random().first()
                vote.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create vote {vote.pk}'))

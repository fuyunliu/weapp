from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from weblog.models import Category, Topic
from follows.models import Follow


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='+', type=int)

    def handle(self, *args, **options):
        count = options['count'][0]
        user_model = get_user_model()

        for _ in range(int(count)):
            try:
                follow = Follow()
                follow.sender = user_model.objects.random().first()
                follow.content_object = user_model.objects.random().first()
                follow.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create follow {follow.pk}'))

        for _ in range(int(count)):
            try:
                follow = Follow()
                follow.sender = user_model.objects.random().first()
                follow.content_object = Category.objects.random().first()
                follow.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create follow {follow.pk}'))

        for _ in range(int(count)):
            try:
                follow = Follow()
                follow.sender = user_model.objects.random().first()
                follow.content_object = Topic.objects.random().first()
                follow.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create follow {follow.pk}'))

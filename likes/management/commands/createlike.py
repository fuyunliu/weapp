from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from weblog.models import Article, Pin
from likes.models import Like


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='+', type=int)

    def handle(self, *args, **options):
        count = options['count'][0]
        user_model = get_user_model()

        for _ in range(int(count)):
            try:
                like = Like()
                like.sender = user_model.objects.random().first()
                like.content_object = Article.objects.random().first()
                like.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create like {like.pk}'))

        for _ in range(int(count)):
            try:
                like = Like()
                like.sender = user_model.objects.random().first()
                like.content_object = Pin.objects.random().first()
                like.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create like {like.pk}'))

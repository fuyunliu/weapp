from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from weblog.models import Article, Pin
from comments.models import Comment
from faker import Faker


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='+', type=int)

    def handle(self, *args, **options):
        count = options['count'][0]
        user_model = get_user_model()
        faker = Faker()

        for _ in range(int(count)):
            fields = {'body': faker.sentence()}
            try:
                comment = Comment(**fields)
                comment.author = user_model.objects.random().first()
                comment.content_object = Article.objects.random().first()
                comment.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create comment {comment.pk}'))

        for _ in range(int(count)):
            fields = {'body': faker.sentence()}
            try:
                comment = Comment(**fields)
                comment.author = user_model.objects.random().first()
                comment.content_object = Pin.objects.random().first()
                comment.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create comment {comment.pk}'))

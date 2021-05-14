from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from weblog.models import Article, Category
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
                'body': faker.text(),
                'status': Article.Status.PUBLISHED
            }
            try:
                article = Article(**fields)
                article.author = user_model.objects.random().first()
                article.category = Category.objects.random().first()
                article.save()
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(str(e)))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully create article {article.pk}'))

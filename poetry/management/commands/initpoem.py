import json
import itertools
from django.core.management.base import BaseCommand
from poetry.models import Author, YouMengYing


def init_author():
    files = [
        'poetry/management/commands/author.tangpoem.json',
        'poetry/management/commands/author.songpoem.json',
        'poetry/management/commands/author.songlyric.json'
    ]
    authors = []
    for file in files:
        with open(file, 'rt', encoding='utf-8') as f:
            data = json.load(f)
            for row in data:
                author = Author(**row)
                authors.append(author)

    batch_size = 1000
    authors = iter(authors)
    while True:
        batch = list(itertools.islice(authors, batch_size))
        if not batch:
            break
        Author.objects.bulk_create(batch, batch_size, ignore_conflicts=True)
        print('ok')


def init_youmengying():
    file = "/Users/fuyun/Personal/chinese-poetry/youmengying/youmengying.json"
    items = []
    with open(file, 'rt', encoding='utf-8') as f:
        data = json.load(f)
        for row in data:
            i = YouMengYing(**row)
            items.append(i)
    batch_size = 1000
    items = iter(items)
    while True:
        batch = list(itertools.islice(items, batch_size))
        if not batch:
            break
        YouMengYing.objects.bulk_create(batch, batch_size, ignore_conflicts=True)
        print('ok')


class Command(BaseCommand):

    def handle(self, *args, **options):
        # init_author()
        init_youmengying()

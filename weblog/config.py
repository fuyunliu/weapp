import types
import collections
from pathlib import Path
import urllib.parse as urlparse

BASE_DIR = Path(__file__).resolve().parent.parent


class Config(collections.UserDict):
    # https://github.com/henriquebastos/python-decouple

    def __init__(self, filename, auto_reload=False):
        super().__init__()
        self.auto_reload = auto_reload
        self.filename = filename
        self._load()
        if self.auto_reload:
            self._settings()

    def _settings(self):
        import importlib
        from django.conf import settings
        from django.conf import LazySettings
        from django.utils.functional import empty

        def __getattr__(self, name):
            if self._wrapped is empty:
                self._setup(name)
            mod = importlib.import_module(self._wrapped.SETTINGS_MODULE)
            val = getattr(mod, 'config')[name] or getattr(self._wrapped, name)
            return val

        LazySettings.__getattr__ = __getattr__
        settings.__dict__.clear()

    def _load(self):
        d = types.ModuleType('config')
        d.__file__ = self.filename

        with open(self.filename, 'rb') as f:
            exec(compile(f.read(), self.filename, 'exec'), d.__dict__)

        for key in dir(d):
            if key.isupper():
                self[key] = getattr(d, key)

        self.old_time = Path(self.filename).stat().st_mtime

    def __getitem__(self, key):
        file_changed = Path(self.filename).stat().st_mtime > self.old_time
        if self.auto_reload and file_changed:
            self._load()
        return super().__getitem__(key)

    def __missing__(self, key):
        return None


SCHEMES = {
    'sqlite': 'django.db.backends.sqlite3',
    'mysql': 'django.db.backends.mysql',
    'postgresql': 'django.db.backends.postgresql',
    'oracle': 'django.db.backends.oracle',
}


def parse_database_url(url):
    # https://github.com/jacobian/dj-database-url
    url = urlparse.urlparse(url)
    config = {
        'ENGINE': SCHEMES[url.scheme],
        'NAME': Path(url.path).name,
        'USER': url.username,
        'PASSWORD': url.password,
        'HOST': url.hostname,
        'PORT': str(url.port)
    }
    return config


config = Config(BASE_DIR / 'weblog' / 'settings.dev')

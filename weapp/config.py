import types
import collections
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def isuppercase(name):
    return name == name.upper() and not name.startswith('_')


def uppercase_attributes(obj):
    return [name for name in dir(obj) if isuppercase(name)]


class Config(collections.UserDict):
    # https://github.com/henriquebastos/python-decouple

    def __init__(self, filename, auto_reload=False):
        super().__init__()
        self.auto_reload = auto_reload
        self.filename = filename
        self._load()
        if self.auto_reload:
            self._settings()

    @staticmethod
    def _settings():
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

        for name in uppercase_attributes(d):
            self[name] = getattr(d, name)

        self.old_time = Path(self.filename).stat().st_mtime

    def __getitem__(self, key):
        file_changed = Path(self.filename).stat().st_mtime > self.old_time
        if self.auto_reload and file_changed:
            self._load()
        return super().__getitem__(key)


config = Config(BASE_DIR / 'weapp' / 'settings.dev')

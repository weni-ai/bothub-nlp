from decouple import config


DEBUG = config('DEBUG', default=False, cast=bool)

SUPPORTED_LANGUAGES = config(
    'SUPPORTED_LANGUAGES',
    cast=lambda v: v.split())

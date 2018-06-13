import plac

from app.settings import SUPPORTED_LANGUAGES
from . import import_langs


@plac.annotations(
    extra_models=('add extra models dir', 'option', 'e'),)
def import_supported_languages(extra_models=None):
    import_langs(extra_models, *SUPPORTED_LANGUAGES)

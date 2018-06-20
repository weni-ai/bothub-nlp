import plac


@plac.annotations(
    extra_models=('add extra models dir', 'option', 'e'),)
def import_supported_languages(extra_models=None):
    from .. import settings
    from .import_langs import import_langs

    import_langs(extra_models, *settings.SUPPORTED_LANGUAGES)

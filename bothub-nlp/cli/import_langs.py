import plac

from . import import_lang


@plac.annotations(
    extra_models=('add extra models dir', 'option', 'e'),)
def import_langs(extra_models=None, *langs):
    print('Languages to import: {}'.format(', '.join(langs)))
    for lang in langs:
        import_lang(extra_models, lang)

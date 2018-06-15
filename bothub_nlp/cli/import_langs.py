import plac


@plac.annotations(
    extra_models=('add extra models dir', 'option', 'e'),)
def import_langs(extra_models=None, *langs):
    from . import import_lang

    print('Languages to import: {}'.format(', '.join(langs)))
    for lang in langs:
        import_lang(extra_models, lang)

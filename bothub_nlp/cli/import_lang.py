import plac


@plac.annotations(
    extra_models=('add extra models dir', 'option', 'e'),)
def import_lang(extra_models=None, lang=None):
    import os
    from spacy.cli import download, link

    print('Importing lang {}'.format(lang))

    if extra_models:
        model_dir_path = os.path.join(extra_models, lang)
        if os.path.isdir(model_dir_path):
            return link(os.path.abspath(model_dir_path), lang, force=True)
    return download(lang)

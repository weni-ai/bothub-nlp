from . import start
from .. import settings

if settings.DEVELOPMENT_MODE:
    import os
    import tornado.autoreload
    tornado.autoreload.start()
    for dir, _, files in os.walk('bothub_nlp'):
        for f in files:
            if not f.startswith('.'):
                tornado.autoreload.watch(
                    '{dir}/{name}'.format(dir=dir, name=f))
start()

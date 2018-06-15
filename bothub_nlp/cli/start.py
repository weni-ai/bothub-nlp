app = None


def load_app():
    from .. import settings
    from ..server import make_app

    global app
    app = make_app()
    app.listen(settings.PORT)


def start():
    import tornado.ioloop

    from .. import settings

    load_app()

    print('Starting server in {} port'.format(settings.PORT))

    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    import os
    import tornado.autoreload

    tornado.autoreload.start()
    for dir, _, files in os.walk('bothub_nlp'):
        for f in files:
            if not f.startswith('.'):
                tornado.autoreload.watch(
                    '{dir}/{name}'.format(dir=dir, name=f))

    start()

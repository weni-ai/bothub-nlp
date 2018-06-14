def start():
    import os
    import tornado.ioloop
    import tornado.autoreload

    from .. import settings
    from ..server import make_app

    global app
    app = make_app()
    app.listen(settings.PORT)

    print('Starting server in {} port'.format(settings.PORT))

    tornado.autoreload.start()
    tornado.autoreload.add_reload_hook(start)
    for dir, _, files in os.walk('static'):
        for f in files:
            if not f.startswith('.'):
                tornado.autoreload.watch('{dir}/{name}'.format(dir=dir, name=f))

    tornado.ioloop.IOLoop.current().start()

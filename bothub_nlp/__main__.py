if __name__ == '__main__':
    import plac
    import sys
    from .cli.import_lang import import_lang
    from .cli.import_langs import import_langs
    from .cli.import_supported_languages import import_supported_languages
    from .cli.start import start

    commands = {
        'import_lang': import_lang,
        'import_langs': import_langs,
        'import_supported_languages': import_supported_languages,
        'start': start,
    }

    if len(sys.argv) == 1:
        print('Available commands: {}'.format(', '.join(commands)))
    else:
        command = sys.argv.pop(1)
        if command in commands:
            plac.call(commands[command], sys.argv[1:])
        else:
            print('Unknown command: {}'.format(command))

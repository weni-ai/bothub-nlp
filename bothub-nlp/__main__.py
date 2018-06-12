if __name__ == '__main__':
    import plac
    import sys
    from .cli import import_lang, import_langs

    commands = {
        'import_lang': import_lang,
        'import_langs': import_langs,
    }

    if len(sys.argv) == 1:
        print('Available commands: {}'.format(', '.join(commands)))
    else:
        command = sys.argv.pop(1)
        if command in commands:
            plac.call(commands[command], sys.argv[1:])
        else:
            print('Unknown command: {}'.format(command))

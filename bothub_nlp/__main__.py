import plac
import sys

commands = {
}

if len(sys.argv) == 1:
    print('Available commands: {}'.format(', '.join(commands)))
else:
    command = sys.argv.pop(1)
    if command in commands:
        plac.call(commands[command], sys.argv[1:])
    else:
        print('Unknown command: {}'.format(command))

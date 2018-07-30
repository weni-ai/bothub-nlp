from . import updateInterpreters


def parse_text(update, text):
    interpreter = updateInterpreters.get(update)
    return interpreter.parse(text)

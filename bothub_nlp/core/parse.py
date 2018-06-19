from . import updateInterpreters

def parse_text(update, text, language=None):
    interpreter = updateInterpreters.get(update)
    return interpreter.parse(text)

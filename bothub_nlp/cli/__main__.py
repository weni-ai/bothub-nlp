import sys
import logging
import plac

from .download_supported_languages import download_supported_languages
from bothub_nlp import settings


logging.basicConfig(
    format=settings.LOGGER_FORMAT,
    level=settings.LOGGER_LEVEL)

commands = {
    'download_supported_languages': download_supported_languages,
}


@plac.annotations(
    command=plac.Annotation(
        help='Command',
        choices=commands.keys()))
def main(command, *command_args):
    plac.call(commands[command], command_args)


plac.call(main, sys.argv[1:])

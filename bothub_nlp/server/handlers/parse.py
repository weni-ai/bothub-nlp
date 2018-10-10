from tornado.web import asynchronous
from tornado.gen import coroutine

from . import ApiHandler
from ..utils import ValidationError
from ..utils import authorization_required
from ..utils import AuthorizationIsRequired
from ... import settings
from ...core.parse import parse_text


class ParseHandler(ApiHandler):
    @asynchronous
    @coroutine
    def get(self):
        text = self.get_argument('text', default=None)
        language = self.get_argument('language', default=None)
        rasa_format = self.get_argument('rasa_format', default=False)

        if not text and not language:
            self.set_header('Content-Type', 'text/plain')
            self.finish('OK')

        self._parse(text, language, rasa_format)

    @asynchronous
    @coroutine
    @authorization_required
    def post(self):
        text = self.get_argument('text', default=None)
        language = self.get_argument('language', default=None)
        rasa_format = self.get_argument('rasa_format', default=False)

        if not text:
            raise ValidationError('text field is required', field='text')

        self._parse(text, language, rasa_format)

    def _parse(self, text, language, rasa_format=False):
        from .. import NEXT_LANGS

        if language and (
            language not in settings.SUPPORTED_LANGUAGES.keys() and
            language not in NEXT_LANGS.keys()
        ):
            raise ValidationError(
                'Language \'{}\' not supported by now.'.format(language),
                field='language')

        repository_authorization = self.repository_authorization()
        if not repository_authorization:
            raise AuthorizationIsRequired()

        repository = repository_authorization.repository
        update = repository.last_trained_update(language)

        if not update:
            next_languages = NEXT_LANGS.get(language, [])
            for next_language in next_languages:
                update = repository.last_trained_update(next_language)
                if update:
                    break

        if not update:
            raise ValidationError(
                'This repository has never been trained',
                field='language')

        answer = parse_text(update, text, rasa_format=rasa_format)
        answer.update({
            'text': text,
            'update_id': update.id,
            'language': update.language,
        })

        self.finish(answer)

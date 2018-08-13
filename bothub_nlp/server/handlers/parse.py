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

        if not text and not language:
            self.set_header('Content-Type', 'text/plain')
            self.finish('OK')

        repository_authorization = self.repository_authorization()
        if not repository_authorization:
            raise AuthorizationIsRequired()

        self._parse(text, language)

    @asynchronous
    @coroutine
    @authorization_required
    def post(self):
        text = self.get_argument('text', default=None)
        language = self.get_argument('language', default=None)

        if not text:
            raise ValidationError('text field is required', field='text')

        self._parse(text, language)

    def _parse(self, text, language):
        if language and language not in settings.SUPPORTED_LANGUAGES.keys():
            raise ValidationError(
                'Language \'{}\' not supported by now.'.format(language),
                field='language')

        repository_authorization = self.repository_authorization()
        repository = repository_authorization.repository
        update = repository.last_trained_update(language)

        if not update:
            raise ValidationError(
                'This repository has never been trained',
                field='language')

        answer = parse_text(update, text)
        answer.update({
            'text': text,
            'update_id': update.id,
            'language': language,
        })

        self.finish(answer)

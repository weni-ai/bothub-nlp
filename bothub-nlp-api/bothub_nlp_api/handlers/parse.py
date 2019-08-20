import tornado.web
from tornado import gen

from bothub_nlp_celery.actions import ACTION_PARSE, queue_name
from bothub_nlp_celery.tasks import TASK_NLU_PARSE_TEXT
from bothub_nlp_celery.app import celery_app
from bothub_nlp import settings as bothub_nlp_settings

from . import ApiHandler
from ..utils import ValidationError
from ..utils import authorization_required
from ..utils import AuthorizationIsRequired


class ParseHandler(ApiHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        text = self.get_argument('text', default=None)
        language = self.get_argument('language', default=None)
        rasa_format = self.get_argument('rasa_format', default=False)

        if not text and not language:
            self.set_header('Content-Type', 'text/plain')
            self.finish('OK')

        self._parse(text, language, rasa_format)

    @tornado.web.asynchronous
    @gen.engine
    @authorization_required
    def post(self):
        text = self.get_argument('text', default=None)
        language = self.get_argument('language', default=None)
        rasa_format = self.get_argument('rasa_format', default=False)

        if not text:
            raise ValidationError('text field is required', field='text')

        self._parse(text, language, rasa_format)

    def _parse(self, text, language, rasa_format=False):
        from ..utils import NEXT_LANGS

        if language and (
            language not in bothub_nlp_settings.SUPPORTED_LANGUAGES.keys() and
            language not in NEXT_LANGS.keys()
        ):
            raise ValidationError(
                'Language \'{}\' not supported by now.'.format(language),
                field='language')

        repository_authorization = self.repository_authorization()
        if not repository_authorization:
            raise AuthorizationIsRequired()
      
        update = self.request_backend_parse('parse', repository_authorization, language)

        if not update.get('update'):
            next_languages = NEXT_LANGS.get(language, [])
            for next_language in next_languages:
                update = self.request_backend_parse('parse', repository_authorization, next_language)
                if update.get('update'):
                    break

        if not update.get('update'):
            raise ValidationError(
                'This repository has never been trained',
                field='language')

        answer_task = celery_app.send_task(
            TASK_NLU_PARSE_TEXT,
            args=[
                update.get('update_id'),
                text,
            ],
            kwargs={
                'rasa_format': rasa_format,
            },
            queue=queue_name(ACTION_PARSE, update.get('language')))
        answer_task.wait()

        answer = answer_task.result
        answer.update({
            'text': text,
            'update_id': update.get('update_id'),
            'language': update.get('language'),
        })

        self.finish(answer)

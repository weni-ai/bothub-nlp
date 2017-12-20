""" This module will train all bots. """
import logging
import json
import uuid
import tornado.escape

from tornado.web import HTTPError, asynchronous
from tornado.gen import coroutine
from rasa_nlu.converters import load_rasa_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer
from slugify import slugify
from app.handlers.base import BothubBaseHandler, SPACY_LANGUAGES
from app.models.models import Repository, Profile, RepositoryAuthorization
from app.models.base_models import DATABASE
from app.settings import DEBUG, OWNER
from app.utils import token_required, MISSING_DATA, DUPLICATE_SLUG, DB_FAIL


logger = logging.getLogger('bothub NLP - Bot Trainer Request Handler')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class BotTrainerRequestHandler(BothubBaseHandler):
    """
    Tornado request handler to train bot.
    """

    @asynchronous
    @coroutine
    @token_required
    def post(self):
        if self.request.body:
            json_body = tornado.escape.json_decode(self.request.body)

            language = json_body.get("language", None)
            bot_slug = json_body.get("slug", None)
            data = json.dumps(json_body.get("data", None))
            private = json_body.get("private", None)

            if None in [language, bot_slug, data, private]:
                raise HTTPError(reason=MISSING_DATA, status_code=401)

            if DEBUG:
                logger.info("Start training bot...")

            with DATABASE.execution_context():
                owner = Profile.select().where(Profile.uuid == uuid.UUID(self.get_cleaned_token()))
                bot = Repository.select().where(Repository.slug == bot_slug)

            if bot.exists():
                raise HTTPError(reason=DUPLICATE_SLUG, status_code=401)

            owner = owner.get()
            config = '{"pipeline": "spacy_sklearn", "path" : "./models", \
                      "data" : "./data.json", "language": "%s"}' % language

            trainer = Trainer(RasaNLUConfig(config), SPACY_LANGUAGES[language])
            trainer.train(load_rasa_data(data))
            bot_data = trainer.persist()
            bot_slug = slugify(bot_slug)
            intents = []
            common_examples = json.loads(data).get('rasa_nlu_data').get('common_examples')

            for common_example in common_examples:
                if common_example.get('intent') not in intents:
                    intents.append(common_example.get('intent'))

            with DATABASE.execution_context():
                repository = Repository.create(bot=bot_data, slug=bot_slug, private=private,
                                               intents=intents, created_by=owner, updated_by=owner)
                repository.save()
                if repository.uuid:
                    authorization = RepositoryAuthorization.create(repository=repository, profile=owner,
                                                                   permission=OWNER, created_by=owner, updated_by=owner)
                    authorization.save()
                    if authorization.uuid:
                        if DEBUG:
                            logger.info("Success bot train...")
                        self.write(dict(repository=repository.to_dict()))
                        self.finish()
                        return

            if DEBUG:
                logger.error("Fail when try insert new bot")

            raise HTTPError(reason=DB_FAIL, status_code=401)
        raise HTTPError(reason=MISSING_DATA, status_code=401)

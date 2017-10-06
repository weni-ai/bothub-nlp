#!/usr/bin/env python
""" This module start server """
from multiprocessing import Queue, Event

import tornado.ioloop
import tornado.escape
import json
import cloudpickle
import redis
import sys
import urllib.request
import psutil
import uuid
import logging
import settings

from threading import Timer, Lock
from tornado.web import Application, asynchronous
from tornado.web import url
from tornado.gen import coroutine
from rasabot import RasaBotProcess, RasaBotTrainProcess
from datetime import datetime, timedelta
from models.models import Bot, Profile
from models.base_models import DATABASE
from decouple import config
from utils import INVALID_TOKEN, DB_FAIL, token_required


logging.basicConfig(filename="bothub-nlp.log")
logger = logging.getLogger('bothub NLP - Bot Manager')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class BotManager():
    """
    Bot mananger responsible to manager all bots in this instance
    """
    _pool = {}

    def __init__(self):
        self.redis = redis.ConnectionPool(
            host=config('BOTHUB_REDIS'),
            port=config('BOTHUB_REDIS_PORT'),
            db=config('BOTHUB_REDIS_DB')
        )
        self._set_instance_redis()
        self._set_server_alive()
        self.start_garbage_collector()

    def _get_bot_data(self, bot_uuid):
        bot_data = {}
        if bot_uuid in self._pool:
            logger.info('Reusing an instance...')
            bot_data = self._pool[bot_uuid]
        else:
            redis_bot = self._get_bot_redis(bot_uuid)
            if redis_bot is not None:
                logger.info('Reusing from redis...')
                redis_bot = cloudpickle.loads(redis_bot)
                bot_data = self._start_bot_process(bot_uuid, redis_bot)
                self._pool[bot_uuid] = bot_data
                self._set_bot_on_instance_redis(bot_uuid)
            else:
                logger.info('Creating a new instance...')

                with DATABASE.execution_context():
                    instance = Bot.get(Bot.uuid == bot_uuid)

                bot = cloudpickle.loads(instance.bot)
                self._set_bot_redis(bot_uuid, cloudpickle.dumps(bot))
                bot_data = self._start_bot_process(bot_uuid, bot)
                self._pool[bot_uuid] = bot_data
                self._set_bot_on_instance_redis(bot_uuid)
        return bot_data

    def _get_new_answer_event(self, bot_uuid):
        return self._get_bot_data(bot_uuid)['new_answer_event']

    def _get_new_question_event(self, bot_uuid):
        return self._get_bot_data(bot_uuid)['new_question_event']

    def _get_questions_queue(self, bot_uuid):
        return self._get_bot_data(bot_uuid)['questions_queue']

    def _get_answers_queue(self, bot_uuid):
        return self._get_bot_data(bot_uuid)['answers_queue']

    def ask(self, question, bot_uuid, auth_token):
        questions_queue = self._get_questions_queue(bot_uuid)
        answers_queue = self._get_answers_queue(bot_uuid)
        questions_queue.put(question)
        new_question_event = self._get_new_question_event(bot_uuid)
        new_question_event.set()
        new_answer_event = self._get_new_answer_event(bot_uuid)

        if not self._pool[bot_uuid]['auth_token'] == auth_token:
            return INVALID_TOKEN

        self._pool[bot_uuid]['last_time_update'] = datetime.now()

        new_answer_event.wait()
        new_answer_event.clear()
        return answers_queue.get()

    def start_bot_process(self, bot_uuid):
        self._get_questions_queue(bot_uuid)

    def start_garbage_collector(self):
        Timer(60.0, self.garbage_collector).start()

    def garbage_collector(self):
        self._set_server_alive()
        with Lock():
            new_pool = {}
            for bot_uuid, bot_instance in self._pool.items():
                if not (datetime.now() - bot_instance['last_time_update']) >= timedelta(minutes=60):
                    self._set_bot_on_instance_redis(bot_uuid)
                    new_pool[bot_uuid] = bot_instance
                else:
                    self._remove_bot_instance_redis(bot_uuid)
                    bot_instance['bot_instance'].terminate()
            self._pool = new_pool
        logger.info("Garbage collected...")
        self._set_usage_memory()
        self.start_garbage_collector()

    def _get_bot_redis(self, bot_uuid):
        return redis.Redis(connection_pool=self.redis).get(bot_uuid)

    def _set_bot_redis(self, bot_uuid, bot):
        return redis.Redis(connection_pool=self.redis).set(bot_uuid, bot)

    def _set_bot_on_instance_redis(self, bot_uuid):
        if redis.Redis(connection_pool=self.redis).set("BOT-%s" % bot_uuid, self.instance_ip, ex=70):
            server_bots = str(
                redis.Redis(connection_pool=self.redis).get("SERVER-%s" % self.instance_ip), "utf-8").split()
            server_bots.append("BOT-%s" % bot_uuid)
            server_bots = " ".join(map(str, server_bots))

            if redis.Redis(connection_pool=self.redis).set("SERVER-%s" % self.instance_ip, server_bots):
                logger.info("Bot set in redis")
                return

        logger.warning("Error on saving bot on Redis instance, trying again...")
        return self._set_bot_on_instance_redis(bot_uuid)

    def _set_instance_redis(self):
        self.instance_ip = str(urllib.request.urlopen(
                                "http://169.254.169.254/latest/meta-data/local-ipv4").read(), "utf-8")
        update_servers = redis.Redis(connection_pool=self.redis).get("SERVERS_INSTANCES_AVAILABLES")

        if update_servers is not None:
            update_servers = str(update_servers, "utf-8").split()
        else:
            update_servers = []

        update_servers.append(self.instance_ip)
        update_servers = " ".join(map(str, update_servers))

        if redis.Redis(connection_pool=self.redis).set("SERVER-%s" % self.instance_ip, "") and \
                redis.Redis(connection_pool=self.redis).set("SERVERS_INSTANCES_AVAILABLES", update_servers):
            logger.info("Set instance in redis")
            return

        logger.critical("Error save instance in redis, trying again")
        return self._set_instance_redis()

    def _remove_bot_instance_redis(self, bot_uuid):
        if redis.Redis(connection_pool=self.redis).delete("BOT-%s" % bot_uuid):
            server_bot_list = str(
                redis.Redis(connection_pool=self.redis).get("SERVER-%s" % self.instance_ip), "utf-8").split()
            server_bot_list.remove("BOT-%s" % bot_uuid)
            server_bot_list = " ".join(map(str, server_bot_list))

            if redis.Redis(connection_pool=self.redis).set("SERVER-%s" % self.instance_ip, server_bot_list):
                logger.info("Removing bot from Redis")
                return

        logger.warning("Error remove bot in instance redis, trying again...")
        return self._remove_bot_instance_redis(bot_uuid)

    def _start_bot_process(self, bot_uuid, model_bot):
        bot_data = {}
        answers_queue = Queue()
        questions_queue = Queue()
        new_question_event = Event()
        new_answer_event = Event()
        bot = RasaBotProcess(questions_queue, answers_queue,
                             new_question_event, new_answer_event, model_bot)
        bot.daemon = True
        bot.start()
        bot_data['bot_instance'] = bot
        bot_data['answers_queue'] = answers_queue
        bot_data['questions_queue'] = questions_queue
        bot_data['new_question_event'] = new_question_event
        bot_data['new_answer_event'] = new_answer_event
        bot_data['last_time_update'] = datetime.now()

        with DATABASE.execution_context():
            bot = Bot.get(Bot.uuid == bot_uuid)
        bot_data['auth_token'] = bot.owner.uuid.hex

        return bot_data

    def _set_server_alive(self):
        if redis.Redis(connection_pool=self.redis).set("SERVER-ALIVE-%s" % self.instance_ip, True, ex=70):
            logger.info("Ping redis, i'm alive")
            return
        logger.warning("Error on ping redis, trying again...")
        return self._set_server_alive()

    def _set_usage_memory(self):
        update_servers = redis.Redis(connection_pool=self.redis).get("SERVERS_INSTANCES_AVAILABLES")
        if update_servers is not None:
            update_servers = str(update_servers, "utf-8").split()
        else:
            update_servers = []

        usage_memory = psutil.virtual_memory().percent
        if usage_memory <= settings.MAX_USAGE_MEMORY:
            if self.instance_ip not in update_servers:
                update_servers.append(self.instance_ip)
        else:
            if self.instance_ip in update_servers:
                update_servers.remove(self.instance_ip)

        update_servers = " ".join(map(str, update_servers))

        if redis.Redis(connection_pool=self.redis).set("SERVERS_INSTANCES_AVAILABLES", update_servers):
            logger.info("Servers set up available")
            return

        logger.warning("Error on set servers availables, trying again...")
        return self._set_usage_memory()


class BotRequestHandler(tornado.web.RequestHandler):
    """
    Tornado request handler to predict data
    """
    @asynchronous
    @coroutine
    @token_required
    def get(self):
        auth_token = self.request.headers.get('Authorization')
        uuid = self.get_argument('uuid', None)
        message = self.get_argument('msg', None)
        if message and uuid:
            answer = bm.ask(message, uuid, auth_token)
            if answer != INVALID_TOKEN:
                data = {
                    'bot_uuid': uuid,
                    'answer': answer
                }
            else:
                data = INVALID_TOKEN
                self.set_status(401)
            self.write(data)
        self.finish()


class BotTrainerRequestHandler(tornado.web.RequestHandler):
    """
    Tornado request handler to train bot
    """
    @asynchronous
    @token_required
    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        auth_token = self.request.headers.get('Authorization')
        language = json_body.get("language", None)
        bot_slug = json_body.get("slug", None)
        data = json.dumps(json_body.get("data", None))
        bot = RasaBotTrainProcess(language, data, self.callback, auth_token, bot_slug)
        bot.daemon = True
        bot.start()

    def callback(self, data):
        if data == INVALID_TOKEN:
            self.set_status(401)
        elif data == DB_FAIL:
            self.set_status(500)
        self.write(json.dumps(data))
        self.finish()


class ProfileRequestHandler(tornado.web.RequestHandler):
    """
    Tornado request handler to predict data
    """
    def _register_profile(self):
        profile = Profile.create()
        profile.save()
        return dict(uuid=profile.uuid.hex)

    @asynchronous
    @coroutine
    @token_required
    def get(self):
        with DATABASE.execution_context():
            owner_profile = Profile.select().where(
                Profile.uuid == uuid.UUID(self.request.headers.get('Authorization')))

            if len(owner_profile) != 1:
                self.set_status(401)
                self.write(INVALID_TOKEN)
                self.finish()

            owner_profile = owner_profile.get()
            bots = Bot.select(Bot.uuid, Bot.slug).where(
                Bot.owner == owner_profile).dicts()

        list_bots = list()
        for bot in bots:
            bot['uuid'] = str(bot['uuid'])
            list_bots.append(bot)
        self.write(json.dumps(list_bots))
        self.finish()

    @asynchronous
    @coroutine
    def post(self):
        with DATABASE.execution_context():
            self.write(self._register_profile())
        self.finish()


def make_app():
    return Application([
        url(r'/auth', ProfileRequestHandler),
        url(r'/bots', BotRequestHandler),
        url(r'/bots-redirect', BotRequestHandler),
        url(r'/train-bot', BotTrainerRequestHandler)
    ])


if __name__ == '__main__':
    bm = BotManager()
    app = make_app()
    app.listen(sys.argv[1])
    tornado.ioloop.IOLoop.current().start()

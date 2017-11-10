#!/usr/bin/env python
""" This module start server """
from multiprocessing import Queue, Event

import cloudpickle
import requests
import psutil

from threading import Timer, Lock

from datetime import datetime, timedelta
from app.rasabot import RasaBotProcess
from app.models.models import Bot
from app.models.base_models import DATABASE
from app.settings import *


class BotManager(object):
    """
    Bot mananger responsible to manager all bots in this instance
    """
    _pool = {}

    def __init__(self, gc=True):
        self.redis = REDIS_CONNECTION
        self._set_instance_redis()
        self._set_server_alive()
        self.gc_test = False
        if not gc:  # pragma: no cover
            self.gc_test = True
        self.start_garbage_collector()

    def _get_bot_data(self, bot_uuid):
        bot_data = {}
        if bot_uuid in self._pool:
            logger.info('Reusing an instance...')
            bot_data = self._pool[bot_uuid]
        else:
            redis_bot = self._get_bot_redis(bot_uuid)
            if redis_bot is not None:  # pragma: no cover
                logger.info('Reusing from redis...')
                redis_bot = cloudpickle.loads(redis_bot)
                bot_data = self._start_bot_process(bot_uuid, redis_bot)
                self._pool[bot_uuid] = bot_data
                self._set_bot_on_instance_redis(bot_uuid)
            else:
                logger.info('Creating a new instance...')

                with DATABASE.execution_context():
                    try:
                        instance = Bot.get(Bot.uuid == bot_uuid)

                        bot = cloudpickle.loads(instance.bot)
                        self._set_bot_redis(bot_uuid, cloudpickle.dumps(bot))
                        bot_data = self._start_bot_process(bot_uuid, bot)
                        self._pool[bot_uuid] = bot_data
                        self._set_bot_on_instance_redis(bot_uuid)
                    except:
                        raise HTTPError(reason=INVALID_BOT, status_code=401)
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

        if not self._pool[bot_uuid]['auth_token'] == auth_token and self._pool[bot_uuid]['private']:
            raise HTTPError(reason=INVALID_TOKEN, status_code=401)

        questions_queue.put(question)
        new_question_event = self._get_new_question_event(bot_uuid)
        new_question_event.set()
        new_answer_event = self._get_new_answer_event(bot_uuid)

        self._pool[bot_uuid]['last_time_update'] = datetime.now()

        new_answer_event.wait()
        new_answer_event.clear()
        return answers_queue.get()

    def start_bot_process(self, bot_uuid):  # pragma: no cover
        self._get_questions_queue(bot_uuid)

    def start_garbage_collector(self):  # pragma: no cover
        Timer(GARBAGE_COLLECTOR_TIMER, self.garbage_collector).start()

    def garbage_collector(self):  # pragma: no cover
        self._set_server_alive()
        with Lock():
            new_pool = {}
            for bot_uuid, bot_instance in self._pool.items():
                if not (datetime.now() - bot_instance['last_time_update']) >= timedelta(minutes=BOT_REMOVER_TIME):
                    self._set_bot_on_instance_redis(bot_uuid)
                    new_pool[bot_uuid] = bot_instance
                else:
                    self._remove_bot_instance_redis(bot_uuid)
                    bot_instance['bot_instance'].terminate()
            self._pool = new_pool
        logger.info("Garbage collected...")
        self._set_usage_memory()
        if not self.gc_test:
            self.start_garbage_collector()

    def _get_bot_redis(self, bot_uuid):
        return redis.Redis(connection_pool=self.redis).get(bot_uuid)

    def _set_bot_redis(self, bot_uuid, bot):
        return redis.Redis(connection_pool=self.redis).set(bot_uuid, bot)

    def _set_bot_on_instance_redis(self, bot_uuid):
        if redis.Redis(connection_pool=self.redis).set("BOT-%s" % bot_uuid, self.instance_ip, ex=SERVER_ALIVE_TIMER):
            server_bots = str(
                redis.Redis(connection_pool=self.redis).get("SERVER-%s" % self.instance_ip), "utf-8").split()
            server_bots.append("BOT-%s" % bot_uuid)
            server_bots = " ".join(map(str, server_bots))

            if redis.Redis(connection_pool=self.redis).set("SERVER-%s" % self.instance_ip, server_bots):
                logger.info("Bot set in redis")
                return

        logger.warning("Error on saving bot on Redis instance, trying again...")  # pragma: no cover
        return self._set_bot_on_instance_redis(bot_uuid)  # pragma: no cover

    def _set_instance_redis(self):
        if not DEBUG:
            self.instance_ip = requests.get(AWS_URL_INSTANCES_INFO).text
        else:
            self.instance_ip = LOCAL_IP

        update_servers = redis.Redis(connection_pool=self.redis).get("SERVERS_INSTANCES_AVAILABLES")

        if update_servers is not None:
            update_servers = str(update_servers, "utf-8").split()
        else:  # pragma: no cover
            update_servers = []

        update_servers.append(self.instance_ip)
        update_servers = " ".join(map(str, update_servers))

        if redis.Redis(connection_pool=self.redis).set("SERVER-%s" % self.instance_ip, "") and \
                redis.Redis(connection_pool=self.redis).set("SERVERS_INSTANCES_AVAILABLES", update_servers):
            logger.info("Set instance in redis")
            return

        logger.critical("Error save instance in redis, trying again")  # pragma: no cover
        return self._set_instance_redis()  # pragma: no cover

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

    @staticmethod
    def _start_bot_process(bot_uuid, model_bot):
        answers_queue = Queue()
        questions_queue = Queue()
        new_question_event = Event()
        new_answer_event = Event()
        bot = RasaBotProcess(questions_queue, answers_queue,
                             new_question_event, new_answer_event, model_bot)
        bot.daemon = True
        bot.start()
        with DATABASE.execution_context():
            bot = Bot.get(Bot.uuid == bot_uuid)

        return {
            'bot_instance': bot,
            'answers_queue': answers_queue,
            'questions_queue': questions_queue,
            'new_question_event': new_question_event,
            'new_answer_event': new_answer_event,
            'last_time_update': datetime.now(),
            'auth_token': bot.owner.uuid.hex,
            'private': bot.private
        }

    def _set_server_alive(self):
        if redis.Redis(connection_pool=self.redis).set("SERVER-ALIVE-%s" % self.instance_ip, True,
                                                       ex=SERVER_ALIVE_TIMER):
            logger.info("Ping redis, i'm alive")
            return
        logger.warning("Error on ping redis, trying again...")  # pragma: no cover
        return self._set_server_alive()  # pragma: no cover

    def _set_usage_memory(self):  # pragma: no cover
        update_servers = redis.Redis(connection_pool=self.redis).get("SERVERS_INSTANCES_AVAILABLES")
        if update_servers is not None:
            update_servers = str(update_servers, "utf-8").split()
        else:
            update_servers = []

        usage_memory = psutil.virtual_memory().percent
        if usage_memory <= MAX_USAGE_MEMORY:
            if self.instance_ip not in update_servers:
                update_servers.append(self.instance_ip)
        else:
            if self.instance_ip in update_servers:
                update_servers.remove(self.instance_ip)

        update_servers = " ".join(map(str, update_servers))

        if redis.Redis(connection_pool=self.redis).set("SERVERS_INSTANCES_AVAILABLES", update_servers):
            logger.info("Servers set up available")
            return

        logger.warning("Error on set servers availables, trying again...")  # pragma: no cover
        return self._set_usage_memory()  # pragma: no cover

""" This module start server """
from multiprocessing import Queue, Event

import tornado.ioloop
import tornado.escape
import json
import os
import cloudpickle
import redis

from threading import Timer, Lock
from tornado.web import Application, asynchronous
from tornado.web import url
from tornado.gen import coroutine
from rasabot import RasaBotProcess, RasaBotTrainProcess
from datetime import datetime, timedelta


class BotManager():
    '''
    javascript client:
    var ws = new WebSocket('ws://localhost:8888/ws');
    ws.onmessage = (evt) => {
        console.log(JSON.parse(evt.data));
    }
    var bot_message = {
        question: 'Whos there?',
        botId: '123456'
    }
    ws.send(JSON.stringify(bot_message))
    '''
    _pool = {}

    def __init__(self):

        self.redis = redis.ConnectionPool(host='localhost', port=6379, db=2)
        self.start_garbage_collector()

    def _get_bot_data(self, bot_uuid):
        bot_data = {}
        if bot_uuid in self._pool:
            print('Reusing an instance...')
            bot_data = self._pool[bot_uuid]
        else:
            redis_bot = self._get_bot_redis(bot_uuid)
            if redis_bot is not None:
                redis_bot = cloudpickle.loads(redis_bot)
                answers_queue = Queue()
                questions_queue = Queue()
                new_question_event = Event()
                new_answer_event = Event()
                bot = RasaBotProcess(questions_queue, answers_queue,
                                    new_question_event, new_answer_event, redis_bot)
                bot.daemon = True
                bot.start()
                bot_data['bot_instance'] = bot
                bot_data['answers_queue'] = answers_queue
                bot_data['questions_queue'] = questions_queue
                bot_data['new_question_event'] = new_question_event
                bot_data['new_answer_event'] = new_answer_event
                bot_data['last_time_update'] = datetime.now()
                self._pool[bot_uuid] = bot_data
            else:
                print('Creating a new instance...')
                model_dir = os.path.abspath('../etc/spacy/%s/model/%s' % # this path is will be changed to get bot in db
                                            (bot_uuid, os.listdir('../etc/spacy/%s/model' % bot_uuid)[0]))

                with open("%s/metadata.pkl" % model_dir, 'rb') as metadata:
                    model = cloudpickle.load(metadata)
                    self._set_bot_redis(bot_uuid, cloudpickle.dumps(model))

                answers_queue = Queue()
                questions_queue = Queue()
                new_question_event = Event()
                new_answer_event = Event()
                bot = RasaBotProcess(questions_queue, answers_queue,
                                    new_question_event, new_answer_event, model)
                bot.daemon = True
                bot.start()
                bot_data['bot_instance'] = bot
                bot_data['answers_queue'] = answers_queue
                bot_data['questions_queue'] = questions_queue
                bot_data['new_question_event'] = new_question_event
                bot_data['new_answer_event'] = new_answer_event
                bot_data['last_time_update'] = datetime.now()
                self._pool[bot_uuid] = bot_data
        return bot_data

    def _get_new_answer_event(self, bot_uuid):
        return self._get_bot_data(bot_uuid)['new_answer_event']

    def _get_new_question_event(self, bot_uuid):
        return self._get_bot_data(bot_uuid)['new_question_event']

    def _get_questions_queue(self, bot_uuid):
        return self._get_bot_data(bot_uuid)['questions_queue']

    def _get_answers_queue(self, bot_uuid):
        return self._get_bot_data(bot_uuid)['answers_queue']

    def ask(self, question, bot_uuid):

        questions_queue = self._get_questions_queue(bot_uuid)
        answers_queue = self._get_answers_queue(bot_uuid)
        questions_queue.put(question)
        new_question_event = self._get_new_question_event(bot_uuid)
        new_question_event.set()
        new_answer_event = self._get_new_answer_event(bot_uuid)

        self._pool[bot_uuid]['last_time_update'] = datetime.now()
        new_answer_event.wait()
        new_answer_event.clear()
        return answers_queue.get()

    def start_bot_process(self, bot_uuid):
        self._get_questions_queue(bot_uuid)

    def start_garbage_collector(self):
        Timer(5*60.0, self.garbage_collector).start()

    def garbage_collector(self):
        with Lock():
            new_pool = {}
            for uuid, bot_instance in self._pool.items():
                if not (datetime.now()-bot_instance['last_time_update']) >= timedelta(minutes=5):
                    new_pool[uuid] = bot_instance
                else:
                    bot_instance['bot_instance'].terminate()
            self._pool = new_pool
        print("garbage collected...")
        self.start_garbage_collector()
    
    def _get_bot_redis(self, bot_uuid):
        return redis.Redis(connection_pool=self.redis).get(bot_uuid)
    
    def _set_bot_redis(self, bot_uuid, bot):
        return redis.Redis(connection_pool=self.redis).set(bot_uuid, bot)    


class BotRequestHandler(tornado.web.RequestHandler):

    @asynchronous
    @coroutine
    def get(self):
        uuid = self.get_argument('uuid', None)
        message = self.get_argument('msg', None)
        if message and uuid:
            answer = bm.ask(message, uuid)
            answer_data = {
                'botId': uuid,
                'answer': answer
            }
            self.write(answer_data)
        self.finish()


class BotTrainerRequestHandler(tornado.web.RequestHandler):

    @asynchronous
    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)

        language = json_body.get("language", None)
        data = json.dumps(json_body.get("data", None))
        bot = RasaBotTrainProcess(language, data, self.callback)
        bot.daemon = True
        bot.start()

    def callback(self, uuid):
        self.write(json.dumps(uuid))
        self.finish()


def make_app():
    return Application([
        url(r'/bots', BotRequestHandler),
        url(r'/train-bot', BotTrainerRequestHandler)
    ])


if __name__ == '__main__':
    bm = BotManager()
    app = make_app()
    app.listen(4000)
    tornado.ioloop.IOLoop.current().start()

""" This module start server """
from multiprocessing import Queue, Event, Manager

import tornado.ioloop
import tornado.escape
import json
import os
import time

from threading import Timer, Lock
from tornado.web import Application, asynchronous
from tornado.web import url
from tornado.gen import coroutine
from rasabot import RasaBot
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
        self.start_garbage_collector()

    def _get_bot_data(self, bot_uuid):
        bot_data = {}
        if bot_uuid in self._pool:
            print('Reusing an instance...')
            bot_data = self._pool[bot_uuid]
        else:
            print('Creating a new instance...')
            rasa_config = '../etc/spacy/%s/config.json' % bot_uuid
            model_dir = os.path.abspath('../etc/spacy/%s/model/%s' % (bot_uuid, os.listdir('../etc/spacy/%s/model' % bot_uuid)[0]))
            data_file = '../etc/spacy/%s/data.json' % bot_uuid
            answers_queue = Queue()
            questions_queue = Queue()
            new_question_event = Event()
            new_answer_event = Event()
            bot = RasaBotProcess(questions_queue, answers_queue, new_question_event, new_answer_event, rasa_config, model_dir, data_file)
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
            self._pool = new_pool
        print("garbage collected...")
        self.start_garbage_collector()


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

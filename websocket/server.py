from tornado.web import Application
from tornado.web import url
from rasabot import RasaBot
from rasabot import RasaBotProcess
from multiprocessing import Queue
from multiprocessing import Event

import psycopg2
import momoko
import json
import time
import tornado.ioloop

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

    def _get_bot_data(self, bot_uuid):
        bot_data = {}
        if bot_uuid in self._pool:
            print('Reusing an instance...')
            bot_data = self._pool[bot_uuid]
        else:
            print('Creating a new instance...')
            rasa_config = '../etc/spacy/%s/config-rasa.json' % bot_uuid
            model_dir = '../etc/spacy/%s/model' % bot_uuid
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
        # Wait for answer...
        # This is not the best aproach! But works for now. ;)
        # while answers_queue.empty():
        #     time.sleep(0.001)
        new_answer_event = self._get_new_answer_event(bot_uuid)
        new_answer_event.wait()
        new_answer_event.clear()
        return answers_queue.get()

    def start_bot_process(self, bot_uuid):
        self._get_questions_queue(bot_uuid)


class BotRequestHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bm = BotManager()

    def check_origin(self, origin):
        return True

    def get(self):
        uuid = self.get_argument('uuid', None)
        message = self.get_argument('msg', None)
        if message and uuid:
            answer = self.bm.ask(message, uuid)
            answer_data = {
                'botId': uuid,
                'answer': answer
            }
            self.write(answer_data)
            self.finish()


def make_app():
    return Application([
        url(r'/bots', BotRequestHandler)
    ])

if __name__ == '__main__':
    app = make_app()
    app.listen(4000)
    tornado.ioloop.IOLoop.current().start()

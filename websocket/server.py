import json
import time
from tornado.websocket import WebSocketHandler
from tornado.web import Application
from tornado.web import url
import tornado.ioloop
from rasabot import RasaBot
from rasabot import RasaBotProcess
from multiprocessing import Queue
from multiprocessing import Event


# class Bot():
#     def ask(self, question):
#         print('A new question arrived to bot: ', question)
#         return "I'm Alfred Pennyworth, at your service Sir!"


class BotManager():
    '''
    Essa é uma versão minimalista do bot manager.

    Desafios a serem superados:

    * - Transformar cada bot em um processo separado.
    * - Implementar mecanismo para troca de mensagens entre o processo pai(BotManager) e seus processos filhos.
    * - Precisaremos de um "bot killer" para matar processos que ultrapassarem o max_lifetime.

    O pacote multiprocessing pode ajudar nessa tarefa.

    Algumas alternativas para essa comunicação são: Pipe, Queue, shared memory e socket

    Qualquer que seja a alternativa escolhida ela deve garantir:
    * - baixa latência
    * - acesso concorrente(mais de um usuário interagindo com o mesmo bot)
    * - sincronismo(pergunta => resposta)

    https://docs.python.org/3.6/library/multiprocessing.html

    Cliente javascript:
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

    def _get_bot_data(self, bot_id):
        bot_data = {}
        if bot_id in self._pool:
            print('Reusing an instance...')
            bot_data = self._pool[bot_id]
        else:
            print('Creating a new instance...')
            ####################### V1
            # bot = RasaBot('../etc/spacy/config.json')
            # bot.trainning('../etc/spacy/data/demo-rasa.json', '../etc/spacy/models/')
            ####################### V2
            rasa_config = '../etc/spacy/config.json'
            model_dir = '../etc/spacy/models/'
            data_file = '../etc/spacy/data/demo-rasa.json'
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
            self._pool[bot_id] = bot_data
        return bot_data

    def _get_new_answer_event(self, bot_id):
        return self._get_bot_data(bot_id)['new_answer_event']

    def _get_new_question_event(self, bot_id):
        return self._get_bot_data(bot_id)['new_question_event']

    def _get_questions_queue(self, bot_id):
        return self._get_bot_data(bot_id)['questions_queue']

    def _get_answers_queue(self, bot_id):
        return self._get_bot_data(bot_id)['answers_queue']

    def ask(self, question, bot_id):
        questions_queue = self._get_questions_queue(bot_id)
        answers_queue = self._get_answers_queue(bot_id)
        questions_queue.put(question)
        new_question_event = self._get_new_question_event(bot_id)
        new_question_event.set()
        # Wait for answer...
        # This is not the best aproach! But works for now. ;)
        # while answers_queue.empty():
        #     time.sleep(0.001)
        new_answer_event = self._get_new_answer_event(bot_id)
        new_answer_event.wait()
        new_answer_event.clear()
        return answers_queue.get()

    def start_bot_process(self, bot_id):
        self._get_questions_queue(bot_id)


class BotWebSocket(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bm = BotManager()

    def check_origin(self, origin):
        return True

    def open(self):
        print('Web socket opened.')
        bot_id = str(self.request.query_arguments['botId'][0])
        self.bm.start_bot_process(bot_id)

    def on_message(self, message):
        print(message)
        print(type(message))
        message_data = json.loads(message)
        question = message_data['question']
        bot_id = message_data['botId']
        self.write_message('Your question was: ', question)
        answer = self.bm.ask(question, bot_id)
        answer_data = {
            'botId': bot_id,
            'answer': answer
        }
        # self.write_message(json.dumps(answer_data))
        self.write_message(answer_data)

    def on_close(self):
        print('Web socket closed.')


def make_app():
    return Application([
        url(r'/ws', BotWebSocket)
    ])

if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

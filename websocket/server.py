import json
from tornado.websocket import WebSocketHandler
from tornado.web import Application
from tornado.web import url
import tornado.ioloop


class Bot():
    def ask(self, question):
        print('A new question arrived to bot: ', question)
        return "I'm Alfred Pennyworth, at your service Sir!"


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

    def _get_bot_instance(self, bot_id):
        bot = None
        if bot_id in self._pool:
            bot = self._pool[bot_id]['bot_instance']
        else:
            bot = Bot()
            bot_data = {
                'bot_instance': bot
            }
            self._pool[bot_id] = bot_data
        return bot

    def ask(self, question, bot_id):
        bot = self._get_bot_instance(bot_id)
        return bot.ask(question)


class BotWebSocket(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bm = BotManager()

    def check_origin(self, origin):
        return True

    def open(self):
        print('Web socket opened.')

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

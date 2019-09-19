import bothub_nlp_api.settings

from flask import jsonify, Flask, Response
from flask import request

from bothub_nlp_api.utils import authorization_required
from bothub_nlp_api.utils import backend
from bothub_nlp_api.utils import get_repository_authorization
from bothub_nlp_api.utils import AuthorizationIsRequired
from bothub_nlp_api.utils import ValidationError

from bothub_nlp_api.handlers import parse
from bothub_nlp_api.handlers import train
from bothub_nlp_api.handlers import evaluate

app = Flask(__name__)


@app.errorhandler(AuthorizationIsRequired)
@app.errorhandler(ValidationError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
@authorization_required
def parse_handler():
    text = request.args.get('text', default=None)
    language = request.args.get('language', default=None)
    rasa_format = request.args.get('rasa_format', default=False)

    if not text and not language:
        return Response('OK', mimetype='text/plain')

    return parse._parse(text, language, rasa_format)


@app.route('/parse/', methods=['POST'])
@authorization_required
def parsepost_handler():
    text = request.args.get('text', default=None)
    language = request.args.get('language', default=None)
    rasa_format = request.args.get('rasa_format', default=False)

    if not text:
        raise ValidationError('text field is required')

    return parse._parse(text, language, rasa_format)


@app.route('/train/', methods=['POST'])
@authorization_required
def train_handler():
    return train.train_handler()


@app.route('/info/')
@authorization_required
def info_handler():
    repository_authorization = get_repository_authorization()
    info = backend().request_backend_parse('info', repository_authorization)
    resp = jsonify(info)
    resp.status_code = 200
    return resp


@app.route('/evaluate/', methods=['POST'])
@authorization_required
def evaluate_handler():
    return evaluate.evaluate_handler()


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=bothub_nlp_api.settings.BOTHUB_NLP_API_SERVER_PORT
    )

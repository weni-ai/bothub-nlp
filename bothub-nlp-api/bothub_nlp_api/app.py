import json

import bothub_nlp_api.settings

from flask import jsonify, Flask, Response
from flask import request
from flask_cors import CORS

from bothub_nlp_api.utils import authorization_required
from bothub_nlp_api.utils import backend
from bothub_nlp_api.utils import get_repository_authorization
from bothub_nlp_api.utils import AuthorizationIsRequired
from bothub_nlp_api.utils import ValidationError

from bothub_nlp_api.handlers import parse
from bothub_nlp_api.handlers import train
from bothub_nlp_api.handlers import evaluate

app = Flask(__name__)
CORS(app)


@app.errorhandler(AuthorizationIsRequired)
@app.errorhandler(ValidationError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/", methods=["GET", "OPTIONS"])
@authorization_required
def parse_handler():
    if request.method == "OPTIONS":
        resp = jsonify({})
        resp.status_code = 204
        return resp
    text = request.args.get("text", default=None)
    language = request.args.get("language", default=None)
    rasa_format = request.args.get("rasa_format", default=False)

    if not text and not language:
        return Response("OK", mimetype="text/plain")

    return parse._parse(text, language, rasa_format)


@app.route("/parse/", methods=["POST", "OPTIONS"])
@authorization_required
def parsepost_handler():
    if request.method == "OPTIONS":
        resp = jsonify({})
        resp.status_code = 204
        return resp

    if len(request.data) > 0:
        jsondata = json.loads(request.data)
        text = jsondata.get("text") if "text" in jsondata else None
        language = jsondata.get("language") if "language" in jsondata else None
        rasa_format = jsondata.get("rasa_format") if "rasa_format" in jsondata else False

    elif len(request.form) > 0:
        text = request.form.get("text") if "text" in request.form else None
        language = request.form.get("language") if "language" in request.form else None
        rasa_format = request.form.get("rasa_format") if "rasa_format" in request.form else False

    else:
        resp = jsonify({})
        resp.status_code = 204
        return resp

    if not text:
        raise ValidationError("text field is required")

    try:
        return parse._parse(text, language, rasa_format)
    except Exception as e:
        resp = jsonify({'error': str(e)})
        resp.status_code = 500
        return resp


@app.route("/train/", methods=["POST", "OPTIONS"])
@authorization_required
def train_handler():
    if request.method == "OPTIONS":
        resp = jsonify({})
        resp.status_code = 204
        return resp
    return train.train_handler()


@app.route("/info/", methods=["GET", "OPTIONS"])
@authorization_required
def info_handler():
    if request.method == "OPTIONS":
        resp = jsonify({})
        resp.status_code = 204
        return resp
    repository_authorization = get_repository_authorization()
    info = backend().request_backend_parse("info", repository_authorization)
    info['intents'] = info['intents_list']
    info.pop('intents_list')
    resp = jsonify(info)
    resp.status_code = 200
    return resp


@app.route("/evaluate/", methods=["POST", "OPTIONS"])
@authorization_required
def evaluate_handler():
    if request.method == "OPTIONS":
        resp = jsonify({})
        resp.status_code = 204
        return resp

    language = None

    if len(request.data) > 0:
        jsondata = json.loads(request.data)
        language = jsondata.get("language") if "language" in jsondata else None

    elif len(request.form) > 0:
        language = request.form.get("language") if "language" in request.form else None

    return evaluate.evaluate_handler(language)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=bothub_nlp_api.settings.BOTHUB_NLP_API_PORT)

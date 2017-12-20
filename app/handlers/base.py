""" Base handler module. """
import traceback
import json
import spacy

from tornado.web import RequestHandler
from app.settings import DEBUG


SPACY_LANGUAGES = {
    'en': spacy.load('en')
}


class BothubBaseHandler(RequestHandler):
    """
    This class is a base request handler,
    others handler will extends of this base handler.
    """
    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        if "exc_info" in kwargs and DEBUG:
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                    'traceback': lines,
                }
            }))
        else:
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                }
            }))

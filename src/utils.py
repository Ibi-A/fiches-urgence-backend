import string
import random
import json

from flask import Response
from http import HTTPStatus


def random_id(size: int) -> str:
    random.seed()
    charset = string.digits + string.ascii_letters + '_'

    generated_id = ''

    for _ in range(0, size):
        generated_id = generated_id + \
            charset[random.randint(0, len(charset) - 1)]

    return generated_id


def http_response(status_code: HTTPStatus, payload: dict) -> Response:
    http_response = Response(
        json.dumps(payload),
        status=status_code.value, mimetype='application/json')

    return http_response

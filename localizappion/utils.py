import base64
from hashlib import sha512

import flask


def create_hash(text):
    hash_data = '{0}+{1}'.format(text, flask.current_app.secret_key)
    return base64.standard_b64encode(sha512(hash_data.encode()).digest()).decode()

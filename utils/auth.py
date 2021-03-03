import json
from flask import request
from functools import wraps
import requests

from app import app
from config.config import RECAPTHA_GOOGLE_URL, SECRET_KEY
from utils.token import decode_token

"""
Этот декоратор проверяет есть ли у нас валидный токен в заголовке
"""
def login_reqiured(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            return {'message': 'Token not exist'}, 403
        token = request.headers.get('Authorization')
        status, error = decode_token(token)
        if status:
            return func(*args, **kwargs)
        else:
            return app.response_class(
                response=json.dumps({'message': error}),
                status=403,
                mimetype='application/json'
            )
    return decorated_function


def check_recaptcha(recaptcha):
    r = requests.post(RECAPTHA_GOOGLE_URL, {'response': recaptcha, 'secret': SECRET_KEY})
    if r.status_code >= 400 or not r.json().get('success'):
        return False
    else:
        return True



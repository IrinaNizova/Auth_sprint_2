import json
from flask import request
from functools import wraps

from app import redis_db_access, app

"""
Этот декоратор проверяет есть ли у нас валидный токен в заголовке
"""
def login_reqiured(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            return {'message': 'Token not exist'}, 403
        token = request.headers.get('Authorization')
        session = redis_db_access.get(token)
        if 'code' in request.get_json(force=True):
            request.get_json(force=True).get('code')
            if session.decode('utf-8') == request.get_json(force=True).get('code'):
                return func(*args, **kwargs)
        elif session.decode('utf-8') == 'True':
            return func(*args, **kwargs)
        else:
            return app.response_class(
                response=json.dumps({'message': 'Login or password is not valid'}),
                status=403,
                mimetype='application/json'
            )
    return decorated_function

import json
from flask import request
from functools import wraps

from app import redis_db, app

"""
Этот декоратор проверяет есть ли у нас валидный токен в заголовке
"""
def login_reqiured(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            return {'message': 'Token not exist'}, 403
        token = request.headers.get('Authorization')
        if 'code' in request.get_json(force=True):
            token += request.get_json(force=True).get('code')
        session = redis_db.get(token)
        if session:
            return func(*args, **kwargs)
        else:
            return app.response_class(
                response=json.dumps({'message': 'Login or password is not valid'}),
                status=403,
                mimetype='application/json'
            )
    return decorated_function

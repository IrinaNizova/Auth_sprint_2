from config import config
from datetime import datetime, timedelta
import jwt
import secrets


def create_access_token(user_id):
    dt = datetime.now() + timedelta(days=1)
    return jwt.encode({
        'id': user_id,
        'exp': str(dt.strftime('%s'))
    }, config.SECRET_KEY, algorithm='HS256')


def create_refresh_token():
    return secrets.token_hex()


def get_user_id_token(token):
    return jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])['id']

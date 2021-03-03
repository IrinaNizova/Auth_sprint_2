from config import config
from datetime import datetime, timedelta
import jwt


AUTH_ACCESS_TOKEN = 'auth_access'
AUTH_REFRESH_TOKEN = 'auth_refresh'


def create_access_token(user_id):
    return create_token(user_id, AUTH_ACCESS_TOKEN, config.TOKEN_TIME)


def create_refresh_token(user_id):
    return create_token(user_id, AUTH_REFRESH_TOKEN, config.REFRESH_TOKEN_TIME)


def create_token(user_id, token_name, time):
    dt = datetime.now() + timedelta(hours=time)
    return jwt.encode({
        'iss': token_name,
        'id': user_id,
        'exp': str(dt.strftime('%s'))
    }, config.SECRET_KEY, algorithm='HS256')


def decode_token(token, token_type=AUTH_ACCESS_TOKEN):
    try:
        decode_token = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    except jwt.exceptions.DecodeError as e:
        return False, e
    if decode_token.get('iss') != token_type:
        print(decode_token.get('iss'), token_type)
        return False, "Not expected token type"
    if not 'id' in decode_token or not 'exp' in decode_token:
        return False, "Not all segments in token"
    if int(decode_token['exp']) < int(datetime.now().strftime('%s')):
        return False, "Outdated token"
    return True, decode_token


def get_user_id_token(token):
    status, result = decode_token(token)
    if not status:
        return None
    return result['id']

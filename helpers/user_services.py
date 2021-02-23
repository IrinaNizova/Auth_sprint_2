from app import redis_db, db
from flask import request
from db.models import User, UserSignIn
import datetime
import bcrypt
import secrets
from config.config import TOKEN_TIME, PIN_CODE_TIME
from helpers.results_map import *
from utils.faker import send_code_to_email, get_random_code
from user_agents import parse


class RedisTokensStorage:
    def __init__(self, redis_adapter=redis_db):
        self.redis_adapter = redis_adapter

    def save_login_token(self, token, time, login) -> None:
        self.redis_adapter.setex(token, time, login)

    def retrieve_login_by_token(self, token) -> str:
        login = self.redis_adapter.get(token)
        return login.decode('utf-8') if login else None

    def del_token(self, token):
        redis_db.delete(token)


tokenStorage = RedisTokensStorage()


class LoginMain:

    def __init__(self, login=None, token=None, code=''):
        if login:
            self.login = login
        elif token:
            self.login = tokenStorage.retrieve_login_by_token(token+code)

    def get_user_by_login(self):
        user = User.query.filter_by(login=self.login).first()
        if not user:
            return LOGIN_NOT_EXIST
        return user


class NewUser:

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def create_new_user(self):
        user = User(login=self.login, password=self.password)
        db.session.add(user)
        db.session.commit()
        return NEW_USER_CREATED


class Login1(LoginMain):

    def __init__(self, login, password):
        super(Login1, self).__init__(login=login)
        self.password = password

    def check_password(self):
        user = self.get_user_by_login()
        if str(user) == LOGIN_NOT_EXIST:
            return LOGIN_NOT_EXIST
        if not user.check_password(self.password):
            return PASSWORD_NOT_VALID

    def create_and_send_pin_code(self):
        pin_code = get_random_code()
        send_code_to_email(pin_code, self.login)
        return pin_code

    def set_temporary_token(self, pin_code):
        token = secrets.token_hex()
        redis_db.setex(token + pin_code, PIN_CODE_TIME, self.login)
        return token

    def start_login(self):
        error = self.check_password()
        if error: return error
        pin_code = self.create_and_send_pin_code()
        token = self.set_temporary_token(pin_code)
        return SEND_PIN_CODE, token


class Login2(LoginMain):

    def __init__(self, pin_code, token):
        super(Login2, self).__init__(token=token, code=pin_code)
        self.pin_code = pin_code
        self.token = token

    def set_standart_token(self, token):
        login = tokenStorage.retrieve_login_by_token(token + self.pin_code)
        tokenStorage.del_token(token)
        tokenStorage.save_login_token(token, TOKEN_TIME, login)

    def get_user_agent_type(self, user_agent):
        user_agent_string = parse(user_agent)
        user_device_type = 'smart'
        if user_agent_string.is_mobile:
            user_device_type = 'mobile'
        elif user_agent_string.is_pc:
            user_device_type = 'web'
        elif user_agent_string.is_tablet:
            user_device_type = 'smart'
        return user_device_type

    def create_login_note(self):
        user = self.get_user_by_login()
        user_agent = request.headers['User-Agent']
        user_device_type = self.get_user_agent_type(user_agent)
        user_sign_in = UserSignIn(user_id=user.id, logined_by=datetime.datetime.now(),
                                  user_agent=user_agent, user_device_type=user_device_type)
        db.session.add(user_sign_in)
        db.session.commit()

    def continue_login(self):
        self.set_standart_token(self.token)
        self.create_login_note()
        return AUTHORIZATION_SUCCESSFUL, self.token


class ChangeLogin(LoginMain):

    def __init__(self, login, old_password, new_password, is_remove_sessions, token):
        super(ChangeLogin, self).__init__(login=login)
        self.old_password = old_password
        self.new_password = new_password
        self.is_remove_sessions = is_remove_sessions
        self.token = token

    def check_eq_login(self):
        redis_login = tokenStorage.retrieve_login_by_token(self.token)
        if redis_login != self.login:
            return NOT_VALID_LOGIN

    def get_and_validate_user_object(self):
        user = self.get_user_by_login()
        if not user.check_password(self.old_password):
            return PASSWORD_NOT_VALID
        return user

    def remove_sessions(self, user_id):
        user_sessions = UserSignIn.query.filter_by(user_id=user_id).all()
        db.session.delete(user_sessions)

    def set_new_login_password(self, user):
        user.login = self.login
        user.password = bcrypt.hashpw(self.new_password.encode('utf-8'), bcrypt.gensalt())
        db.session.commit()

    def perform_change_login(self):
        error = self.check_eq_login()
        if error: return error
        user = self.get_and_validate_user_object()
        if str(user) == PASSWORD_NOT_VALID:
            return PASSWORD_NOT_VALID
        if self.is_remove_sessions:
            self.remove_sessions(user.id)
        self.set_new_login_password(user)
        return LOGIN_AND_PASSWORD_CHANGED_SUCCESSFUL


class Sessions(LoginMain):

    def __init__(self, token):
        super(Sessions, self).__init__(token=token)

    def get_sessions_by_user(self):
        user = self.get_user_by_login()
        user_sessions = UserSignIn.query.filter_by(user_id=user.id).all()
        return [u.to_dict() for u in user_sessions]


def logout(token):
    tokenStorage.del_token(token)


def create_refresh(old_token):
    login = tokenStorage.retrieve_login_by_token(old_token)
    tokenStorage.del_token(old_token)
    token = secrets.token_hex()
    tokenStorage.save_login_token(token, TOKEN_TIME, login)
    return NEW_TOKEN_CREATED, token

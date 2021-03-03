from app import redis_db_invalid_tokens, redis_db_pin_codes, db
from flask import request
from db.models import User, UserSignIn, Roles, RolesForUser
import datetime
import bcrypt
from config.config import TOKEN_TIME, PIN_CODE_TIME, REFRESH_TOKEN_TIME
from helpers.results_map import *
from utils.auth import check_recaptcha
from utils.faker import send_code_to_email, get_random_code
from user_agents import parse
from utils.token import create_access_token, create_refresh_token, get_user_id_token, decode_token, AUTH_REFRESH_TOKEN


def get_user_by_login(login):
    user = User.query.filter_by(login=login).first()
    if not user:
        return LOGIN_NOT_EXIST
    return user


class NewUser:

    def __init__(self, login, password, roles=None, recaptcha=None):
        self.login = login
        self.password = password
        self.roles = roles or []
        self.recaptcha = recaptcha

    def create_new_user(self):
        if self.recaptcha:
            if not check_recaptcha(self.recaptcha):
                return CAPTURE_NOT_VALID
        user = User(login=self.login, password=self.password)
        db.session.add(user)
        for role in self.roles:
            role_obj = Roles.query.filter_by(name=role).first()
            if role_obj:
                rfu = RolesForUser(user_id=user.id, role_id=role_obj.id)
                db.session.add(rfu)
        db.session.commit()
        return NEW_USER_CREATED


class Login1:

    def __init__(self, login, password):
        self.login=login
        self.password = password

    def check_password(self):
        user = get_user_by_login(self.login)
        if str(user) == LOGIN_NOT_EXIST:
            return LOGIN_NOT_EXIST
        if not user.check_password(self.password):
            return PASSWORD_NOT_VALID

    def create_and_send_pin_code(self):
        pin_code = get_random_code()
        send_code_to_email(pin_code, self.login)
        return pin_code

    def start_login(self):
        error = self.check_password()
        if error: return error
        pin_code = self.create_and_send_pin_code()
        redis_db_pin_codes.setex(self.login, PIN_CODE_TIME, pin_code)
        return SEND_PIN_CODE


class Login2:

    def __init__(self, login, pin_code):
        self.login = login
        self.pin_code = pin_code

    def set_tokens(self):
        access_token = create_access_token(self.login)
        refresh_token = create_refresh_token(self.login)
        return access_token, refresh_token

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
        user = get_user_by_login(self.login)
        user_agent = request.headers['User-Agent']
        user_device_type = self.get_user_agent_type(user_agent)
        user_sign_in = UserSignIn(user_id=user.id, logined_by=datetime.datetime.now(),
                                  user_agent=user_agent, user_device_type=user_device_type)
        db.session.add(user_sign_in)
        db.session.commit()

    def continue_login(self):
        pin_code = redis_db_pin_codes.get(self.login)
        if not pin_code:
            return NOT_VALID_LOGIN
        if self.pin_code != pin_code.decode('utf-8'):
            return CODE_NOT_EXIST
        access_token, refresh_token = self.set_tokens()
        self.create_login_note()
        return AUTHORIZATION_SUCCESSFUL, access_token, refresh_token


class ChangeLogin:

    def __init__(self, login, old_password, new_password, is_remove_sessions, token):
        self.login = login
        self.old_password = old_password
        self.new_password = new_password
        self.is_remove_sessions = is_remove_sessions
        self.token = token

    def check_eq_login(self):
        redis_login = get_user_id_token(self.token)
        if redis_login != self.login:
            return NOT_VALID_LOGIN

    def get_and_validate_user_object(self):
        user = get_user_by_login(self.login)
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


class Sessions:

    def __init__(self, token):
        self.login = get_user_id_token(token)

    def get_sessions_by_user(self):
        user = get_user_by_login(self.login)
        user_sessions = UserSignIn.query.filter_by(user_id=user.id).all()
        return [u.to_dict() for u in user_sessions]


def logout(token, refresh_token=None):
    if refresh_token:
        redis_db_invalid_tokens.set(refresh_token, "Invalid")
    redis_db_invalid_tokens.set(token, "Invalid")


def create_refresh(refresh_token, access_token):
    invalid_token = redis_db_invalid_tokens.get(refresh_token)
    if invalid_token:
        return NOT_VALID_TOKEN
    status, token_dict = decode_token(refresh_token, token_type=AUTH_REFRESH_TOKEN)
    if not status:
        return NOT_VALID_TOKEN
    redis_db_invalid_tokens.set(access_token, "Invalid")
    new_access_token = create_access_token(token_dict['id'])
    new_refresh_token = create_refresh_token(token_dict['id'])
    return NEW_TOKEN_CREATED, new_access_token, new_refresh_token


def add_role_to_user(token, role):
    login = get_user_id_token(token)
    user_obj = User.query.filter_by(login=login).first()
    role_obj = Roles.query.filter_by(name=role).first()
    rfu = RolesForUser(user_id=user_obj.id, role_id=role_obj.id)
    db.session.add(rfu)
    db.session.commit()


def delete_role_to_user(token, role):
    login = get_user_id_token(token)
    user_obj = User.query.filter_by(login=login).first()
    role_obj = Roles.query.filter_by(name=role).first()
    rfu = RolesForUser.query.filter_by(user_id=user_obj.id, role_id=role_obj.id)
    db.session.delete(rfu)
    db.session.commit()

from flask import request
from flask_restful import Resource

from utils.auth import login_reqiured
from helpers.results_map import CODES_MAP, CODE_NOT_EXIST, NEW_TOKEN_CREATED
from helpers.schemas import ChangeLoginSchema, LoginSchema
import helpers.user_services as us
from marshmallow.exceptions import ValidationError


class New(Resource):

    """
    Создаём нового пользователя
    """
    def post(self):
        args = request.get_json(force=True)
        try:
            LoginSchema().load(dict(args))
        except ValidationError as e:
            return {'message': e.args}, 400
        result = us.NewUser(login=args.get('login'), password=args.get('password'), roles=args.get('roles'), recaptcha=args.get('roles')).create_new_user()

        return {'message': result}, CODES_MAP[result]


class Login(Resource):

    """
    Логинимся. Передаём логин и пароль, нам вернётся токен и сторонний сервис пришлёт пин-код
    """
    def post(self):
        args = request.get_json(force=True)
        try:
            LoginSchema().load(dict(args))
        except ValidationError as e:
            return {'message': e.args}, 400
        result = us.Login1(login=args.get('login'), password=args.get('password')).start_login()
        return {'message': result}, CODES_MAP[result]


class Login2(Resource):

    def post(self):
        """
        Отправляем логин и пин-код. Если в заголовках правильный токен - мы успешно залогинились
        """
        args = request.get_json(force=True)

        code = args.get('code')
        login = args.get('login')
        if not code:
            return {'message': CODE_NOT_EXIST}, CODES_MAP[CODE_NOT_EXIST]

        result = us.Login2(pin_code=code, login=login).continue_login()
        if isinstance(result, tuple):
            message, access_token, refresh_token = result
            return {'message': message, 'access_token': access_token, 'refresh_token': refresh_token}, CODES_MAP[message]
        else:
            return {'message': result}, CODES_MAP[result]


class Sessions(Resource):

    @login_reqiured
    def get(self):
        """
        Этот метод возвращает информацию о всех заходах на сервис данного пользователя
        ---
        responses:
         200:
           description: A single user item
           schema:
             id: UserSignIn
             properties:
               logined_by:
                 type: datetime
                 description: Time for log in
               user_agent:
                type: string
                description: user agent string
               user_device_type:
                type: string
                description: device type - smart, mobile or web from user agent
        """
        users_sessions = us.Sessions(request.headers.get('Authorization')).get_sessions_by_user()
        return {'message': "Session list received", 'sessions': users_sessions}


class Logout(Resource):

    @login_reqiured
    def post(self):
        """
        Сессия данного пользователя становится неактивна
        :return:
        """
        token = request.headers.get('Authorization')
        refresh_token = request.headers.get('Refresh')
        us.logout(token, refresh_token)
        return {'message': "Logout successful"}


class ChangeLogin(Resource):

    @login_reqiured
    def post(self):
        """
        Можно сменить логин или пароль
        :return:
        """
        login = request.json.get('login')
        password = request.json.get('password')
        new_password = request.json.get('new_password')
        is_remove_sessions = request.json.get('is_remove_sessions')
        try:
            ChangeLoginSchema().load(dict(request.json))
        except ValidationError as e:
            return {'message': e.args}, 400
        token = request.headers.get('Authorization')
        result = us.ChangeLogin(login, password, new_password, is_remove_sessions, token).perform_change_login()
        return {'message': result}, CODES_MAP[result]


class RefreshToken(Resource):

    @login_reqiured
    def post(self):
        """
        Обновляем токен. Старый становится неактивен
        :return:
        новый токен
        """
        result = us.create_refresh(refresh_token=request.headers.get('Refresh'), access_token=request.headers.get('Authorization'))
        if isinstance(result, tuple):
            return {'message': result[0], 'access_token': result[1], 'refresh_token': result[2]}, CODES_MAP[result[0]]
        else:
            return {'message': result}, CODES_MAP[result]

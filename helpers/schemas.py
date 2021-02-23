from flask_restful import abort
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow.exceptions import ValidationError

from app import app


ma = Marshmallow(app)


class LoginSchema(ma.SQLAlchemyAutoSchema):

    login = fields.String(required=True)
    password = fields.String(required=True)


class ChangeLoginSchema(ma.SQLAlchemyAutoSchema):

    login = fields.String(required=True)
    password = fields.String(required=True)
    new_password = fields.String(required=True)
    is_remove_sessions = fields.String()


def validate_login(args):

    try:
        LoginSchema().load(dict(args))
    except ValidationError as e:
        abort(400, message=e.args)


def validate_change_login(args):

    try:
        ChangeLoginSchema().load(dict(args))
    except ValidationError as e:
        abort(400, message=e.args)

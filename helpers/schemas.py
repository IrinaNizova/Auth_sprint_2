from flask_marshmallow import Marshmallow
from marshmallow import fields

from app import app


ma = Marshmallow(app)


class LoginSchema(ma.SQLAlchemyAutoSchema):

    login = fields.String(required=True)
    password = fields.String(required=True)
    roles = fields.List(cls_or_instance=int)


class ChangeLoginSchema(ma.SQLAlchemyAutoSchema):

    login = fields.String(required=True)
    password = fields.String(required=True)
    new_password = fields.String(required=True)
    is_remove_sessions = fields.String()


class RoleSchema(ma.SQLAlchemySchema):
    id = fields.String(required=True)
    name = fields.String(required=True)




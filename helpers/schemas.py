from flask_marshmallow import Marshmallow
from marshmallow import fields

from app import app


ma = Marshmallow(app)


class LoginSchema(ma.SQLAlchemyAutoSchema):

    login = fields.String(required=True)
    password = fields.String(required=True)
    roles = fields.List(cls_or_instance=fields.Integer)


class ChangeLoginSchema(ma.SQLAlchemyAutoSchema):

    login = fields.String(required=True)
    password = fields.String(required=True)
    new_password = fields.String(required=True)
    is_remove_sessions = fields.String()


class RoleSchema(ma.SQLAlchemySchema):
    id = fields.String(required=True)
    name = fields.String(required=True)


class PermissionSchema(ma.SQLAlchemySchema):
    id = fields.String(required=True)
    name = fields.String(required=True)


class PermissionsForRolesSchema(ma.SQLAlchemySchema):
    role = fields.String(required=True)
    permission = fields.String(required=True)
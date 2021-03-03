from flask import Blueprint, request, abort
from flask_restful import Resource
from marshmallow.exceptions import ValidationError

from db.models import Roles, Permissions, PermissionsForRoles
from helpers.schemas import PermissionsForRolesSchema
from app import db
from helpers.schemas import RoleSchema
from utils.auth import login_reqiured
from helpers.user_services import add_role_to_user, delete_role_to_user

r = Blueprint('r', __name__)


@r.route('/user/add_role', methods=['POST'])
@login_reqiured
def add_role():
    args = request.get_json(force=True)
    add_role_to_user(request.headers.get('Authorization'), args['role'])
    return {"message": "Add role successful"}

@r.route('/user/del_role', methods=['POST'])
@login_reqiured
def delete_role():
    args = request.get_json(force=True)
    delete_role_to_user(request.headers.get('Authorization'), args['role'])
    return {"message": "Delete role successful"}


@r.route('/role/add_perm', methods=['POST'])
def add_permission_to_role():
    args = request.get_json(force=True)
    try:
        PermissionsForRolesSchema().load(dict(args))
    except ValidationError as e:
        return {'message': e.args}, 400
    role = Roles.query.filter_by(name=args['role']).first()
    permission = Permissions.query.filter_by(name=args['permission']).first()
    if not role or not permission:
        return {'message': "Not such role or permission"}, 400
    pfr = PermissionsForRoles(permission_id=permission.id, role_id=role.id)
    db.session.add(pfr)
    db.session.commit()
    return {"message": "Add permission to role"}


@r.route('/role/del_perm', methods=['POST'])
def del_permission_to_role():
    args = request.get_json(force=True)
    role = Roles.query.filter_by(name=args['role']).first()
    permission = Permissions.query.filter_by(name=args['permission']).first()
    if not role or not permission:
        return {'message': "Not such role or permission"}, 400
    pfr = PermissionsForRoles.query.filter_by(permission_id=permission.id, role_id=role.id).first()
    if not pfr:
        return {'message': "Not such relation"}, 400
    db.session.delete(pfr)
    db.session.commit()
    return {"message": "Delete permission to role"}


class RoleAPI(Resource):

    def post(self):
        args = request.get_json(force=True)
        if not args.get('name'):
            abort(400, "Not name")
        if Roles.query.filter_by(name=args['name']).first():
            abort(400, "This role exists")
        role = Roles(name=args['name'])
        db.session.add(role)
        db.session.commit()
        return {"message": "Role created successful"}, 201

    def delete(self):
        args = request.get_json(force=True)
        role = Roles.query.filter_by(name=args['name']).first()
        if not role:
            abort(400, "This role not exists")
        db.session.delete(role)
        db.session.commit()

    def get(self):
        roles = Roles.query.all()
        schema = RoleSchema(many=True)
        result = schema.dump(roles)
        return result

    def put(self):
        args = request.get_json(force=True)
        role = Roles.query.filter_by(name=args['old_name']).first()
        role.name = args['new_name']
        db.session.commit()



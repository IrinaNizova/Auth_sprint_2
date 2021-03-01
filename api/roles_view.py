from flask import request, abort
from flask_restful import Resource
from db.models import Roles
from app import db
from helpers.schemas import RoleSchema


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

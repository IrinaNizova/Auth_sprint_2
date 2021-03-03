from flask import request, abort
from flask_restful import Resource
from db.models import Permissions
from app import db
from helpers.schemas import PermissionSchema


class PermissionAPI(Resource):

    def post(self):
        args = request.get_json(force=True)
        if not args.get('name'):
            abort(400, "Not name")
        if Permissions.query.filter_by(name=args['name']).first():
            abort(400, "This permission exists")
        role = Permissions(name=args['name'])
        db.session.add(role)
        db.session.commit()
        return {"message": "Permission created successful"}, 201

    def delete(self):
        args = request.get_json(force=True)
        role = Permissions.query.filter_by(name=args['name']).first()
        if not role:
            abort(400, "This permission not exists")
        db.session.delete(role)
        db.session.commit()

    def get(self):
        roles = Permissions.query.all()
        schema = PermissionSchema(many=True)
        result = schema.dump(roles)
        return result

    def put(self):
        args = request.get_json(force=True)
        role = Permissions.query.filter_by(name=args['old_name']).first()
        role.name = args['new_name']
        db.session.commit()

from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from .extensions import db
from .models import User
from .schemas import CredentialsSchema, UserSchema


def credentials():
    data = CredentialsSchema().load(request.get_json())
    data["email"] = data["email"].strip().lower()
    return data


class RegisterResource(Resource):
    def post(self):
        try:
            data = credentials()
        except ValidationError as error:
            return {"errors": error.messages}, 400
        user = User(email=data["email"])
        user.set_password(data["password"])
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "El correo ya está registrado."}, 409
        return UserSchema().dump(user), 201


class LoginResource(Resource):
    def post(self):
        try:
            data = credentials()
        except ValidationError as error:
            return {"errors": error.messages}, 400
        user = db.session.scalar(db.select(User).filter_by(email=data["email"]))
        if user is None or not user.check_password(data["password"]):
            return {"message": "Credenciales incorrectas."}, 401
        return {"access_token": create_access_token(identity=str(user.id))}, 200


class ProfileResource(Resource):
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        if not isinstance(identity, str) or not identity.isdecimal():
            return {"message": "Identidad inválida."}, 401
        user = db.session.get(User, int(identity))
        if user is None:
            return {"message": "Usuario no encontrado."}, 404
        return UserSchema().dump(user), 200

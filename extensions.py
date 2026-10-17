from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()


# Toda falla de autenticación responde 401 (por defecto un token mal firmado da 422).
@jwt.unauthorized_loader
def sin_token(motivo):
    return {"msg": "Falta el token Bearer", "detalle": motivo}, 401


@jwt.invalid_token_loader
def token_invalido(motivo):
    return {"msg": "Token inválido", "detalle": motivo}, 401


@jwt.expired_token_loader
def token_vencido(_header, _payload):
    return {"msg": "Token vencido"}, 401

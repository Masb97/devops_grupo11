from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Blacklist
from schemas import consulta_schema, entrada_schema


def ip_cliente():
    # Detrás del ALB, remote_addr es la IP interna del balanceador/proxy.
    # El ALB pone la IP del cliente en X-Forwarded-For ("cliente, proxy1, ...").
    xff = request.headers.get("X-Forwarded-For", "")
    return xff.split(",")[0].strip() or request.remote_addr or "desconocida"


class BlacklistCollection(Resource):
    method_decorators = [jwt_required()]

    def post(self):
        cuerpo = request.get_json(silent=True)
        if cuerpo is None:
            return {"msg": "El cuerpo debe ser JSON"}, 400
        try:
            datos = entrada_schema.load(cuerpo)
        except ValidationError as err:
            return {"msg": "Datos inválidos", "errores": err.messages}, 400

        registro = Blacklist(
            email=datos["email"].strip().lower(),
            app_uuid=str(datos["app_uuid"]),
            blocked_reason=datos["blocked_reason"],
            ip=ip_cliente(),
        )
        db.session.add(registro)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"msg": "El email ya estaba en la lista negra"}, 409
        return {"msg": "Email agregado a la lista negra", "id": registro.id}, 201


class BlacklistItem(Resource):
    method_decorators = [jwt_required()]

    def get(self, email):
        registro = Blacklist.query.filter_by(email=email.strip().lower()).first()
        return consulta_schema.dump({
            "email": email,
            "is_blacklisted": registro is not None,
            "blocked_reason": registro.blocked_reason if registro else None,
        }), 200

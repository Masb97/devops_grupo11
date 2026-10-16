"""Punto de entrada. Beanstalk (Python en Amazon Linux 2023) busca el objeto
`application` en el módulo `application` (WSGIPath por defecto)."""
import os

from flask import Flask
from flask_jwt_extended import create_access_token
from flask_restful import Api
from sqlalchemy import exc

from config import Config
from extensions import db, jwt, ma
from instancia import INSTANCE_ID
from resources import BlacklistCollection, BlacklistItem

# La versión viaja DENTRO del .zip: cambiar este archivo y subir un .zip nuevo
# es un despliegue de aplicación (lo que mide la deployment policy).
_RAIZ = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_RAIZ, "VERSION"), encoding="utf-8") as f:
    APP_VERSION = f.read().strip()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    api = Api(app)
    api.add_resource(BlacklistCollection, "/blacklists")
    api.add_resource(BlacklistItem, "/blacklists/<string:email>")

    @app.get("/ping")
    def ping():
        # Health check del balanceador: no toca la base de datos.
        return "pong", 200

    @app.get("/version")
    def version():
        # Para medir despliegues: qué versión y qué instancia respondió.
        return {"version": APP_VERSION, "instance": INSTANCE_ID}

    @app.cli.command("crear-token")
    def crear_token():
        """Imprime un JWT sin vencimiento firmado con JWT_SECRET_KEY."""
        print(create_access_token(identity="blacklist-clients", expires_delta=False))

    with app.app_context():
        try:
            db.create_all()
        except exc.SQLAlchemyError as e:
            # Con varias instancias arrancando a la vez, otra pudo crear la tabla
            # primero; o la base aún no es alcanzable. /ping sigue respondiendo.
            db.session.rollback()
            app.logger.warning("create_all no se completó: %s", e)

    return app


application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)

import os
from datetime import timedelta
import click
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_restful import Api
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .extensions import db, ma, jwt


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    database_url = os.getenv("DATABASE_URL", "")
    for prefix in ("postgres://", "postgresql://"):
        if database_url.startswith(prefix):
            database_url = database_url.replace(prefix, "postgresql+psycopg://", 1)
            break
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=30),
        MAX_CONTENT_LENGTH=16384,
    )
    if test_config:
        app.config.update(test_config)
    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("Configura DATABASE_URL en el entorno o en .env")
    if not app.config["JWT_SECRET_KEY"] or len(app.config["JWT_SECRET_KEY"]) < 32:
        raise RuntimeError("JWT_SECRET_KEY debe contener al menos 32 caracteres")
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    from .resources import RegisterResource, LoginResource, ProfileResource
    api = Api(app)
    api.add_resource(RegisterResource, "/api/auth/register")
    api.add_resource(LoginResource, "/api/auth/login")
    api.add_resource(ProfileResource, "/api/me")

    @app.get("/")
    def index():
        return jsonify(application="devops_proyecto", health="/health",
                       endpoints=["/api/auth/register", "/api/auth/login", "/api/me"])

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify(status="unavailable"), 503
        return jsonify(status="ok")

    @app.cli.command("init-db")
    def init_db():
        """Crea las tablas iniciales; no reemplaza migraciones."""
        db.create_all()
        click.echo("Tablas creadas.")

    return app

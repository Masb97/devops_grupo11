"""Configuración leída del entorno (Twelve-Factor, factor III)."""
import os

from sqlalchemy.engine import URL


def _database_url():
    # 1) DATABASE_URL completa, p. ej. postgresql://usuario:clave@host:5432/blacklist
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    # 2) Variables RDS_* (los nombres que usa Beanstalk). URL.create escapa
    #    caracteres especiales de la contraseña.
    if os.getenv("RDS_HOSTNAME"):
        return URL.create(
            "postgresql+psycopg2",
            username=os.getenv("RDS_USERNAME"),
            password=os.getenv("RDS_PASSWORD"),
            host=os.environ["RDS_HOSTNAME"],
            port=int(os.getenv("RDS_PORT", "5432")),
            database=os.getenv("RDS_DB_NAME", "postgres"),
        ).render_as_string(hide_password=False)
    # 3) Desarrollo local sin Postgres.
    return "sqlite:///local.db"


class Config:
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "solo-para-desarrollo-cambiame")
    # Flask-RESTful se traga las excepciones de Flask-JWT-Extended (las vuelve 500)
    # si no se propagan.
    PROPAGATE_EXCEPTIONS = True
    # Tildes legibles en las respuestas JSON de Flask-RESTful.
    RESTFUL_JSON = {"ensure_ascii": False}

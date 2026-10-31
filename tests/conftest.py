import os
from pathlib import Path

_DB = Path(__file__).resolve().parent / "test_blacklist.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_DB}"
os.environ["JWT_SECRET_KEY"] = "clave-de-prueba-solo-para-la-suite-local"

import pytest
from flask_jwt_extended import create_access_token

from application import application
from extensions import db


@pytest.fixture
def cliente():
    application.config.update(TESTING=True)
    with application.app_context():
        db.drop_all()
        db.create_all()
    with application.test_client() as cliente_http:
        yield cliente_http
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def token():
    with application.app_context():
        return create_access_token(identity="blacklist-clients", expires_delta=False)

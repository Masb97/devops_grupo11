from sqlalchemy.exc import SQLAlchemyError

from application import application, create_app
from config import _database_url
from instancia import leer_instance_id


def test_crear_token_imprime_un_jwt():
    resultado = application.test_cli_runner().invoke(args=["crear-token"])
    assert resultado.exit_code == 0
    assert resultado.output.strip().count(".") == 2


def test_create_all_no_impide_arrancar(monkeypatch, caplog):
    def falla():
        raise SQLAlchemyError("base no disponible")

    monkeypatch.setattr("application.db.create_all", falla)
    with caplog.at_level("WARNING"):
        app = create_app()
    assert app is not None
    assert "create_all no se completó" in caplog.text


def test_database_url_desde_variables_rds(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("RDS_HOSTNAME", "db.ejemplo.internal")
    monkeypatch.setenv("RDS_USERNAME", "blacklist")
    monkeypatch.setenv("RDS_PASSWORD", "p@ss:word")
    monkeypatch.setenv("RDS_PORT", "5432")
    monkeypatch.setenv("RDS_DB_NAME", "blacklist")
    url = _database_url()
    assert url.startswith("postgresql+psycopg2://")
    assert "db.ejemplo.internal" in url
    assert "blacklist" in url


def test_database_url_sqlite_si_no_hay_entorno(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("RDS_HOSTNAME", raising=False)
    assert _database_url() == "sqlite:///local.db"


class _Respuesta:
    def __init__(self, contenido):
        self._contenido = contenido

    def read(self):
        return self._contenido


def test_leer_instance_id_en_ec2(monkeypatch):
    respuestas = iter([_Respuesta(b"token-imds"), _Respuesta(b"i-0123456789abcdef0")])
    monkeypatch.setattr(
        "instancia.urllib.request.urlopen",
        lambda *args, **kwargs: next(respuestas),
    )
    assert leer_instance_id() == "i-0123456789abcdef0"


def test_leer_instance_id_fuera_de_ec2(monkeypatch):
    def falla(*args, **kwargs):
        raise OSError("sin metadatos")

    monkeypatch.setattr("instancia.urllib.request.urlopen", falla)
    assert leer_instance_id().startswith("local-")

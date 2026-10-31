from datetime import timedelta

from flask_jwt_extended import create_access_token

from application import application
from extensions import db
from models import Blacklist
from resources import ip_cliente
CUERPO = {
    "email": "ana@ejemplo.com",
    "app_uuid": "11111111-1111-1111-1111-111111111111",
    "blocked_reason": "prueba unitaria",
}


def autorizacion(token):
    return {"Authorization": f"Bearer {token}"}


def test_ping_responde_pong(cliente):
    respuesta = cliente.get("/ping")
    assert respuesta.status_code == 200
    assert respuesta.data == b"pong"


def test_version_informa_la_version_desplegada(cliente):
    from pathlib import Path

    esperada = Path("VERSION").read_text(encoding="utf-8").strip()
    respuesta = cliente.get("/version")
    cuerpo = respuesta.get_json()
    assert respuesta.status_code == 200
    assert cuerpo["version"] == esperada
    assert isinstance(cuerpo["instance"], str) and cuerpo["instance"]


def test_post_blacklists_agrega_email(cliente, token):
    respuesta = cliente.post("/blacklists", json=CUERPO, headers=autorizacion(token))
    assert respuesta.status_code == 201
    cuerpo = respuesta.get_json()
    assert cuerpo["msg"] == "Email agregado a la lista negra"
    assert isinstance(cuerpo["id"], int)

    with application.app_context():
        registro = db.session.get(Blacklist, cuerpo["id"])
        assert registro.email == "ana@ejemplo.com"
        assert registro.ip == "127.0.0.1"
        assert registro.blocked_reason == "prueba unitaria"


def test_post_blacklists_normaliza_email_y_toma_ip_del_balanceador(cliente, token):
    respuesta = cliente.post(
        "/blacklists",
        json={
            "email": "Ana@Ejemplo.com",
            "app_uuid": "22222222-2222-2222-2222-222222222222",
            "blocked_reason": None,
            "campo_extra": "se ignora",
        },
        headers={**autorizacion(token), "X-Forwarded-For": "203.0.113.9, 10.0.0.4"},
    )
    assert respuesta.status_code == 201
    with application.app_context():
        registro = Blacklist.query.filter_by(email="ana@ejemplo.com").one()
        assert registro.ip == "203.0.113.9"
        assert registro.blocked_reason is None


def test_post_blacklists_sin_motivo_lo_deja_vacio(cliente, token):
    respuesta = cliente.post(
        "/blacklists",
        json={
            "email": "sin-motivo@ejemplo.com",
            "app_uuid": "33333333-3333-3333-3333-333333333333",
        },
        headers=autorizacion(token),
    )
    assert respuesta.status_code == 201


def test_post_blacklists_rechaza_cuerpo_que_no_es_json(cliente, token):
    respuesta = cliente.post(
        "/blacklists",
        data="no-json",
        headers={**autorizacion(token), "Content-Type": "text/plain"},
    )
    assert respuesta.status_code == 400
    assert respuesta.get_json()["msg"] == "El cuerpo debe ser JSON"


def test_post_blacklists_rechaza_datos_invalidos(cliente, token):
    respuesta = cliente.post(
        "/blacklists",
        json={"email": "no-es-un-email", "app_uuid": "123", "blocked_reason": "x" * 256},
        headers=autorizacion(token),
    )
    assert respuesta.status_code == 400
    cuerpo = respuesta.get_json()
    assert cuerpo["msg"] == "Datos inválidos"
    assert "email" in cuerpo["errores"]
    assert "app_uuid" in cuerpo["errores"]
    assert "blocked_reason" in cuerpo["errores"]


def test_post_blacklists_rechaza_email_duplicado(cliente, token):
    primero = cliente.post("/blacklists", json=CUERPO, headers=autorizacion(token))
    assert primero.status_code == 201
    duplicado = cliente.post("/blacklists", json=CUERPO, headers=autorizacion(token))
    assert duplicado.status_code == 409
    assert duplicado.get_json()["msg"] == "El email ya estaba en la lista negra"


def test_post_blacklists_exige_token(cliente):
    respuesta = cliente.post("/blacklists", json=CUERPO)
    assert respuesta.status_code == 401
    assert respuesta.get_json()["msg"] == "Falta el token Bearer"


def test_get_blacklists_exige_token(cliente):
    respuesta = cliente.get("/blacklists/ana@ejemplo.com")
    assert respuesta.status_code == 401
    assert respuesta.get_json()["msg"] == "Falta el token Bearer"


def test_blacklists_rechaza_token_invalido(cliente):
    respuesta = cliente.get(
        "/blacklists/ana@ejemplo.com",
        headers={"Authorization": "Bearer esto-no-es-un-jwt"},
    )
    assert respuesta.status_code == 401
    assert respuesta.get_json()["msg"] == "Token inválido"


def test_blacklists_rechaza_token_vencido(cliente):
    with application.app_context():
        vencido = create_access_token(identity="blacklist-clients", expires_delta=timedelta(seconds=-1))
    respuesta = cliente.get(
        "/blacklists/ana@ejemplo.com",
        headers=autorizacion(vencido),
    )
    assert respuesta.status_code == 401
    assert respuesta.get_json()["msg"] == "Token vencido"


def test_get_blacklists_email_limpio(cliente, token):
    respuesta = cliente.get(
        "/blacklists/limpio@ejemplo.com",
        headers=autorizacion(token),
    )
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        "email": "limpio@ejemplo.com",
        "is_blacklisted": False,
        "blocked_reason": None,
    }


def test_get_blacklists_email_bloqueado(cliente, token):
    alta = cliente.post("/blacklists", json=CUERPO, headers=autorizacion(token))
    assert alta.status_code == 201
    respuesta = cliente.get(
        "/blacklists/ANA@ejemplo.com",
        headers=autorizacion(token),
    )
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        "email": "ANA@ejemplo.com",
        "is_blacklisted": True,
        "blocked_reason": "prueba unitaria",
    }


def test_ip_cliente_sin_origen_conocido():
    with application.test_request_context(environ_overrides={"REMOTE_ADDR": ""}):
        assert ip_cliente() == "desconocida"

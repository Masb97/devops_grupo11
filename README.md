# devops_grupo11 · Lista negra global de emails

Microservicio REST en Python 3.13 con Flask, Flask SQLAlchemy, Flask RESTful,
Flask Marshmallow, Flask JWT Extended, Werkzeug y PostgreSQL. Se despliega a mano
en AWS Elastic Beanstalk (entorno con balanceador y Auto Scaling de 3 a 6
instancias) contra una base AWS RDS PostgreSQL. Entrega 1 del curso DevOps (MISO).

## API

| Método | Ruta | Función |
| --- | --- | --- |
| POST | `/blacklists` | Agrega un email a la lista negra global |
| GET | `/blacklists/<email>` | Indica si el email está en la lista y el motivo |
| GET | `/ping` | Health check del balanceador (no consulta la base) |
| GET | `/version` | Versión desplegada e ID de la instancia que respondió |

Los dos endpoints de `/blacklists` exigen `Authorization: Bearer <token>`. El token
es estático: un JWT sin vencimiento firmado con `JWT_SECRET_KEY`, que se genera
una sola vez con `flask --app application crear-token`.

`POST /blacklists` recibe JSON con `email` (obligatorio), `app_uuid` (UUID
obligatorio) y `blocked_reason` (opcional, máximo 255 caracteres). Guarda además
la IP de origen (cabecera `X-Forwarded-For` del balanceador) y la fecha/hora.
Responde 201, 400 (datos inválidos), 401 (sin token o token inválido) o 409 (el
email ya estaba).

## Ejecutar localmente

```sh
docker run --rm --name pg-blacklist -p 5432:5432 \
  -e POSTGRES_USER=blacklist -e POSTGRES_PASSWORD=blacklist -e POSTGRES_DB=blacklist \
  postgres:17-alpine

uv venv --python 3.13 .venv && source .venv/bin/activate
uv pip install -r requirements.txt
export DATABASE_URL=postgresql://blacklist:blacklist@localhost:5432/blacklist
export JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
flask --app application run --port 5000
```

La tabla se crea al arrancar. Sin `DATABASE_URL` ni variables `RDS_*`, la app usa
SQLite local.

## Despliegue en Elastic Beanstalk

```sh
git archive --format=zip -o ../blacklist-v1.zip HEAD
```

Subir el `.zip` desde la consola de Beanstalk (plataforma Python 3.13 sobre Amazon
Linux 2023). Variables de entorno del entorno: `JWT_SECRET_KEY` y `DATABASE_URL`
(o `RDS_HOSTNAME`, `RDS_PORT`, `RDS_DB_NAME`, `RDS_USERNAME`, `RDS_PASSWORD`).
`.ebextensions/01-healthcheck.config` apunta el health check a `/ping`. Para medir
una estrategia de despliegue, cambiar `VERSION` y subir un `.zip` nuevo.

No subir `.env` ni credenciales al repositorio.

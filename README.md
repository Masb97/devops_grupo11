# devops_proyecto

Base de aplicación web y API REST en Python 3.12 con Flask, Flask SQLAlchemy,
Flask RESTful, Flask Marshmallow, Flask JWT Extended, Werkzeug y PostgreSQL.
Gunicorn sirve la aplicación en producción.

El enunciado recibido define el stack, pero no incluye las funcionalidades de
negocio. Esta base implementa registro, login y perfil protegido como punto de
partida; no constituye la aplicación final del proyecto académico.

## Ejecutar localmente

Desde esta carpeta, con PostgreSQL instalado y una base `devops_proyecto` creada:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -c 'import secrets; print(secrets.token_hex(32))'
# Copiar el secreto generado a JWT_SECRET_KEY y ajustar DATABASE_URL en .env.
flask --app wsgi init-db
flask --app wsgi run
```

`init-db` crea tablas nuevas sin borrar datos. Para cambios posteriores al modelo,
incorporar migraciones antes de desplegar. No activar el depurador en producción.

## API

| Método | Ruta | Función |
| --- | --- | --- |
| GET | `/` | Información de la aplicación |
| GET | `/health` | Verifica conexión SQL; 503 si falla |
| POST | `/api/auth/register` | Registra un usuario |
| POST | `/api/auth/login` | Emite JWT con duración de 30 minutos |
| GET | `/api/me` | Devuelve el perfil autenticado |

Registro y login reciben JSON con `email` y `password` (8 a 128 caracteres).
Las contraseñas se almacenan como hashes de Werkzeug; nunca se serializan.

```sh
curl -X POST http://localhost:5000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"usuario@example.com","password":"clave-segura-123"}'
curl -X POST http://localhost:5000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"usuario@example.com","password":"clave-segura-123"}'
curl http://localhost:5000/api/me -H 'Authorization: Bearer REEMPLAZAR_TOKEN'
```

## Despliegue PaaS: Render

Configuración preparada para servicio web y PostgreSQL administrado. No se ha
realizado ningún despliegue ni creado recursos en la nube.

1. Subir el repositorio a un proveedor Git conectado a Render.
2. Crear un Blueprint y seleccionar `render.yaml` como ruta.
3. Revisar los planes y sus costos antes de crear los recursos. El comando
   `preDeployCommand` requiere un plan compatible con comandos previos al despliegue.
4. La aplicación está en la raíz del repositorio; el Blueprint no requiere `rootDir`.
5. Verificar `/health`, registro, login y perfil en la URL HTTPS asignada.

El secreto JWT se genera en el proveedor y la conexión se inyecta desde PostgreSQL.
No subir `.env` ni credenciales al repositorio. Para uso público, añadir límites de
intentos de autenticación y las funcionalidades de negocio solicitadas.

Documentación oficial:
- https://render.com/docs/blueprint-spec
- https://render.com/docs/postgresql-creating-connecting
- https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage.html

## Pruebas

```sh
python -m unittest discover -s tests -v
```

Las pruebas usan SQLite en memoria únicamente para comprobar la API; el entorno
local y PaaS usan PostgreSQL. Validar además la conexión real antes de la entrega.

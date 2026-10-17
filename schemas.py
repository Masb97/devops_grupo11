from marshmallow import EXCLUDE, fields, validate

from extensions import ma


class BlacklistEntradaSchema(ma.Schema):
    """Valida el cuerpo del POST /blacklists."""

    class Meta:
        unknown = EXCLUDE  # ignora campos extra en lugar de fallar

    email = fields.Email(required=True)
    app_uuid = fields.UUID(required=True)
    blocked_reason = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=255)
    )


class BlacklistConsultaSchema(ma.Schema):
    """Forma de la respuesta del GET /blacklists/<email>."""

    email = fields.String()
    is_blacklisted = fields.Boolean()
    blocked_reason = fields.String(allow_none=True)


entrada_schema = BlacklistEntradaSchema()
consulta_schema = BlacklistConsultaSchema()

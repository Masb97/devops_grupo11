from marshmallow import fields, validate
from .extensions import ma


class CredentialsSchema(ma.Schema):
    email = fields.Email(required=True, validate=validate.Length(max=254))
    password = fields.String(required=True, load_only=True,
                             validate=validate.Length(min=8, max=128))


class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(dump_only=True)

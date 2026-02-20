from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class TokenResponseSchema(Schema):
    access_token = fields.Str(required=True)

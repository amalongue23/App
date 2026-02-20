from marshmallow import Schema, fields


class UserCreateSchema(Schema):
    full_name = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    role = fields.Str(required=True)


class UserResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str()
    username = fields.Str()
    role = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime()

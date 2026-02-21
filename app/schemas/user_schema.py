from marshmallow import Schema, fields


class UserCreateSchema(Schema):
    full_name = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    role = fields.Str(required=True)


class UserUpdateSchema(Schema):
    full_name = fields.Str()
    username = fields.Str()
    password = fields.Str(load_only=True)
    role = fields.Str()
    is_active = fields.Bool()


class UserResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str()
    username = fields.Str()
    role = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime()


class UserActivityResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    actor_id = fields.Int(allow_none=True)
    actor_username = fields.Method("get_actor_username")
    action = fields.Str()
    description = fields.Str()
    created_at = fields.DateTime()

    def get_actor_username(self, obj):
        return obj.actor.username if getattr(obj, "actor", None) else None


class UserActivityQuerySchema(Schema):
    module = fields.Str(load_default=None)
    action = fields.Str(load_default=None)
    q = fields.Str(load_default=None)
    days = fields.Int(load_default=None)
    limit = fields.Int(load_default=200)

from marshmallow import Schema, fields, validate


class UserCreateSchema(Schema):
    full_name = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    role = fields.Str(required=True)
    unit_id = fields.Int(load_default=None, allow_none=True)
    department_id = fields.Int(load_default=None, allow_none=True)
    photo_url = fields.Str(load_default=None, allow_none=True)
    birth_date = fields.Date(load_default=None, allow_none=True)
    sex = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(["M", "F"]))


class UserUpdateSchema(Schema):
    full_name = fields.Str()
    username = fields.Str()
    password = fields.Str(load_only=True)
    role = fields.Str()
    is_active = fields.Bool()
    unit_id = fields.Int(load_default=None, allow_none=True)
    department_id = fields.Int(load_default=None, allow_none=True)
    photo_url = fields.Str(load_default=None, allow_none=True)
    birth_date = fields.Date(load_default=None, allow_none=True)
    sex = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(["M", "F"]))


class UserResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str()
    username = fields.Str()
    role = fields.Str()
    photo_url = fields.Str(allow_none=True)
    birth_date = fields.Date(allow_none=True)
    sex = fields.Str(allow_none=True)
    unit_id = fields.Method("get_unit_id")
    department_id = fields.Method("get_department_id")
    is_active = fields.Bool()
    created_at = fields.DateTime()

    def get_unit_id(self, obj):
        scope = getattr(obj, "scope", None)
        return scope.unit_id if scope else None

    def get_department_id(self, obj):
        scope = getattr(obj, "scope", None)
        return scope.department_id if scope else None


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

from marshmallow import Schema, fields


class UnitCreateSchema(Schema):
    name = fields.Str(required=True)
    code = fields.Str(required=True)
    description = fields.Str(allow_none=True)


class UnitUpdateSchema(Schema):
    name = fields.Str()
    code = fields.Str()
    description = fields.Str(allow_none=True)


class UnitResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    code = fields.Str()
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime()

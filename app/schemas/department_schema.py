from marshmallow import Schema, fields


class DepartmentCreateSchema(Schema):
    name = fields.Str(required=True)
    code = fields.Str(required=True)
    unit_id = fields.Int(required=True)


class DepartmentUpdateSchema(Schema):
    name = fields.Str()
    code = fields.Str()
    unit_id = fields.Int()


class DepartmentResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    code = fields.Str()
    unit_id = fields.Int()
    created_at = fields.DateTime()

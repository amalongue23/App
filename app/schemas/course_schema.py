from marshmallow import Schema, fields


class CourseCreateSchema(Schema):
    name = fields.Str(required=True)
    code = fields.Str(required=True)
    department_id = fields.Int(required=True)
    credits = fields.Int(required=True)


class CourseUpdateSchema(Schema):
    name = fields.Str()
    code = fields.Str()
    department_id = fields.Int()
    credits = fields.Int()


class CourseResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    code = fields.Str()
    department_id = fields.Int()
    credits = fields.Int()
    created_at = fields.DateTime()

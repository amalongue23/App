from marshmallow import Schema, fields


class AcademicYearCreateSchema(Schema):
    year_label = fields.Str(required=True)


class AcademicYearResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    year_label = fields.Str()
    is_open = fields.Bool()
    opened_at = fields.DateTime()
    closed_at = fields.DateTime(allow_none=True)

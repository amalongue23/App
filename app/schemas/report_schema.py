from marshmallow import Schema, fields


class ReportRequestSchema(Schema):
    report_type = fields.Str(required=True)
    params = fields.Dict(required=False)


class ReportResponseSchema(Schema):
    report_type = fields.Str(required=True)
    rows = fields.List(fields.Dict(), required=True)

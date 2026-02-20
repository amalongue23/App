from marshmallow import Schema, fields


class UnifySourcesSchema(Schema):
    sources = fields.List(fields.List(fields.Dict()), required=True)


class DatasetValidateSchema(Schema):
    dataset = fields.List(fields.Dict(), required=True)


class DatasetValidationErrorSchema(Schema):
    index = fields.Int(required=True)
    error = fields.Str(required=True)


class DatasetRunResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    source_count = fields.Int()
    consolidated_data = fields.List(fields.Dict())
    validation_errors = fields.List(fields.Dict())
    created_at = fields.DateTime()


class DatasetValidationResponseSchema(Schema):
    errors = fields.List(fields.Nested(DatasetValidationErrorSchema))

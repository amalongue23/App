from marshmallow import Schema, fields, validate


class StudentCreateSchema(Schema):
    full_name = fields.Str(required=True)
    registration_number = fields.Str(required=True)
    email = fields.Email(required=True)
    department_id = fields.Int(required=True)
    course_id = fields.Int(required=True)
    birth_date = fields.Date(required=True)
    sex = fields.Str(required=True, validate=validate.OneOf(["M", "F"]))


class StudentUpdateSchema(Schema):
    full_name = fields.Str()
    registration_number = fields.Str()
    email = fields.Email()
    department_id = fields.Int()
    course_id = fields.Int()
    birth_date = fields.Date()
    sex = fields.Str(validate=validate.OneOf(["M", "F"]))


class StudentResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str()
    registration_number = fields.Str()
    email = fields.Email()
    department_id = fields.Int()
    course_id = fields.Int()
    course_name = fields.Method("get_course_name")
    birth_date = fields.Date(allow_none=True)
    sex = fields.Str(allow_none=True)
    created_at = fields.DateTime()

    def get_course_name(self, obj):
        return obj.course.name if getattr(obj, "course", None) else None


class StudentControlCreateSchema(Schema):
    department_id = fields.Int(required=True)
    academic_year_id = fields.Int(required=True)


class StudentControlResponseSchema(Schema):
    department_id = fields.Int()
    academic_year_id = fields.Int()
    created_records = fields.Int()
    total_students = fields.Int()


class StudentStatusUpdateSchema(Schema):
    academic_year_id = fields.Int(required=True)
    status = fields.Str(required=True)


class StudentStatusQuerySchema(Schema):
    academic_year_id = fields.Int(required=True)


class StudentStatusResponseSchema(Schema):
    student_id = fields.Int()
    academic_year_id = fields.Int()
    status = fields.Str()
    updated_at = fields.DateTime(allow_none=True)


class StudentStatusListResponseSchema(Schema):
    student_id = fields.Int()
    status = fields.Str()

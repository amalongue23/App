from marshmallow import Schema, fields, validate

ACADEMIC_LEVELS = [
    "LICENCIATURA_1",
    "LICENCIATURA_2",
    "LICENCIATURA_3",
    "LICENCIATURA_4",
    "LICENCIATURA_5",
    "MESTRADO_1",
    "MESTRADO_2",
]


class StudentCreateSchema(Schema):
    full_name = fields.Str(required=True)
    registration_number = fields.Str(required=True)
    email = fields.Email(required=True)
    department_id = fields.Int(required=True)
    course_id = fields.Int(required=True)
    birth_date = fields.Date(required=True)
    sex = fields.Str(required=True, validate=validate.OneOf(["M", "F"]))
    academic_level = fields.Str(required=True, validate=validate.OneOf(ACADEMIC_LEVELS))


class StudentUpdateSchema(Schema):
    full_name = fields.Str()
    registration_number = fields.Str()
    email = fields.Email()
    department_id = fields.Int()
    course_id = fields.Int()
    birth_date = fields.Date()
    sex = fields.Str(validate=validate.OneOf(["M", "F"]))
    academic_level = fields.Str(validate=validate.OneOf(ACADEMIC_LEVELS))


class StudentResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str()
    registration_number = fields.Str()
    email = fields.Email()
    department_id = fields.Int()
    course_id = fields.Int()
    course_name = fields.Method("get_course_name")
    academic_level = fields.Str(allow_none=True)
    academic_level_label = fields.Method("get_academic_level_label")
    birth_date = fields.Date(allow_none=True)
    sex = fields.Str(allow_none=True)
    created_at = fields.DateTime()

    def get_course_name(self, obj):
        return obj.course.name if getattr(obj, "course", None) else None

    def get_academic_level_label(self, obj):
        labels = {
            "LICENCIATURA_1": "1º ano de Licenciatura",
            "LICENCIATURA_2": "2º ano de Licenciatura",
            "LICENCIATURA_3": "3º ano de Licenciatura",
            "LICENCIATURA_4": "4º ano de Licenciatura",
            "LICENCIATURA_5": "5º ano de Licenciatura",
            "MESTRADO_1": "1º ano de Mestrado",
            "MESTRADO_2": "2º ano de Mestrado",
        }
        return labels.get(getattr(obj, "academic_level", None), None)


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
    academic_level = fields.Str(required=False, validate=validate.OneOf(ACADEMIC_LEVELS))


class StudentStatusQuerySchema(Schema):
    academic_year_id = fields.Int(required=True)


class StudentStatusResponseSchema(Schema):
    student_id = fields.Int()
    academic_year_id = fields.Int()
    status = fields.Str()
    academic_level = fields.Str(allow_none=True)
    academic_level_label = fields.Method("get_academic_level_label")
    updated_at = fields.DateTime(allow_none=True)

    def get_academic_level_label(self, obj):
        value = obj.get("academic_level") if isinstance(obj, dict) else getattr(obj, "academic_level", None)
        labels = {
            "LICENCIATURA_1": "1º ano de Licenciatura",
            "LICENCIATURA_2": "2º ano de Licenciatura",
            "LICENCIATURA_3": "3º ano de Licenciatura",
            "LICENCIATURA_4": "4º ano de Licenciatura",
            "LICENCIATURA_5": "5º ano de Licenciatura",
            "MESTRADO_1": "1º ano de Mestrado",
            "MESTRADO_2": "2º ano de Mestrado",
        }
        return labels.get(value, None)


class StudentStatusListResponseSchema(Schema):
    student_id = fields.Int()
    status = fields.Str()
    academic_level = fields.Str(allow_none=True)


from marshmallow import Schema, fields

class DirectorDashboardStatisticsSchema(Schema):
    unit = fields.Dict(required=True)
    kpis = fields.Dict(required=True)
    performance = fields.List(fields.Dict(), required=True)
    trends = fields.List(fields.Dict(), required=True)
    departments = fields.List(fields.Dict(), required=True)
    activities = fields.List(fields.Dict(), required=True)
    notices = fields.List(fields.Dict(), required=True)
    statistics = fields.Dict(required=True)


class ChiefDashboardQuerySchema(Schema):
    ano_academico_id = fields.Int(required=True)
    ano_lectivo = fields.Str(required=True)
    unit_id = fields.Int(load_default=None)
    department_id = fields.Int(load_default=None)
    course_id = fields.Int(load_default=None)


class DashboardAcademicYearSchema(Schema):
    ano_academico_id = fields.Int(required=True)
    ano_lectivo = fields.Str(required=True)


class DashboardFiltersResponseSchema(Schema):
    anos = fields.List(fields.Nested(DashboardAcademicYearSchema), required=True)
    units = fields.List(fields.Dict(), required=True)
    departments = fields.List(fields.Dict(), required=True)
    courses = fields.List(fields.Dict(), required=True)


class ChiefDashboardResponseSchema(Schema):
    department = fields.Dict(required=True)
    kpis = fields.Dict(required=True)
    performance = fields.List(fields.Dict(), required=True)
    trends = fields.List(fields.Dict(), required=True)
    statistics = fields.Dict(required=True)
    courses = fields.List(fields.Dict(), required=True)
    activities = fields.List(fields.Dict(), required=True)
    notices = fields.List(fields.Dict(), required=True)


class DirectorDashboardResponseSchema(Schema):
    unit = fields.Dict(required=True)
    kpis = fields.Dict(required=True)
    performance = fields.List(fields.Dict(), required=True)
    trends = fields.List(fields.Dict(), required=True)
    departments = fields.List(fields.Dict(), required=True)
    activities = fields.List(fields.Dict(), required=True)
    notices = fields.List(fields.Dict(), required=True)


class RectorDashboardResponseSchema(Schema):
    institution = fields.Dict(required=True)
    kpis = fields.Dict(required=True)
    performance = fields.List(fields.Dict(), required=True)
    distribution = fields.List(fields.Dict(), required=True)
    units = fields.List(fields.Dict(), required=True)
    activities = fields.List(fields.Dict(), required=True)
    notices = fields.List(fields.Dict(), required=True)


class AdminDashboardResponseSchema(Schema):
    kpis = fields.Dict(required=True)
    series = fields.Dict(required=True)
    role_distribution = fields.List(fields.Dict(), required=True)
    recent_activities = fields.List(fields.Dict(), required=True)
    technical = fields.Dict(required=True)

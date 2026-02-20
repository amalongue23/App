from flask.views import MethodView
from flask_smorest import Blueprint

from app.auth.decorators import roles_required
from app.schemas.course_schema import CourseCreateSchema, CourseResponseSchema, CourseUpdateSchema
from app.services.course_service import CourseService


blp = Blueprint("Courses", "courses", url_prefix="/api/courses", description="Courses")
service = CourseService()


@blp.route("")
class CourseCollectionResource(MethodView):
    @roles_required("REITOR", "DIRETOR", "CHEFE")
    @blp.arguments(CourseCreateSchema)
    @blp.response(201, CourseResponseSchema)
    def post(self, payload):
        return service.create(payload)


@blp.route("/<int:course_id>")
class CourseResource(MethodView):
    @roles_required("REITOR", "DIRETOR", "CHEFE")
    @blp.arguments(CourseUpdateSchema)
    @blp.response(200, CourseResponseSchema)
    def put(self, payload, course_id):
        return service.update(course_id, payload)


@blp.route("/by-department/<int:department_id>")
class CourseByDepartmentResource(MethodView):
    @roles_required("REITOR", "DIRETOR", "CHEFE")
    @blp.response(200, CourseResponseSchema(many=True))
    def get(self, department_id):
        return service.list_by_department(department_id)

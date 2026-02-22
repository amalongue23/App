from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint

from app.auth.decorators import roles_required
from app.schemas.student_schema import (
    StudentControlCreateSchema,
    StudentControlResponseSchema,
    StudentCreateSchema,
    StudentResponseSchema,
    StudentStatusListResponseSchema,
    StudentStatusQuerySchema,
    StudentStatusUpdateSchema,
    StudentStatusResponseSchema,
    StudentUpdateSchema,
)
from app.services.student_service import StudentService


blp = Blueprint("Students", "students", url_prefix="/api/students", description="Students")
service = StudentService()


@blp.route("")
class StudentCollectionResource(MethodView):
    @roles_required("REITOR", "DIRETOR", "CHEFE", "ADMIN")
    @blp.arguments(StudentCreateSchema)
    @blp.response(201, StudentResponseSchema)
    def post(self, payload):
        user_id = int(get_jwt_identity())
        return service.create(user_id=user_id, data=payload)


@blp.route("/<int:student_id>")
class StudentResource(MethodView):
    @roles_required("REITOR", "DIRETOR", "CHEFE", "ADMIN")
    @blp.response(200, StudentResponseSchema)
    def get(self, student_id):
        user_id = int(get_jwt_identity())
        return service.get_by_id(user_id=user_id, student_id=student_id)

    @roles_required("REITOR", "DIRETOR", "CHEFE", "ADMIN")
    @blp.arguments(StudentUpdateSchema)
    @blp.response(200, StudentResponseSchema)
    def put(self, payload, student_id):
        user_id = int(get_jwt_identity())
        return service.update(user_id=user_id, student_id=student_id, data=payload)


@blp.route("/by-department/<int:department_id>")
class StudentByDepartmentResource(MethodView):
    @roles_required("REITOR", "DIRETOR", "CHEFE", "ADMIN")
    @blp.response(200, StudentResponseSchema(many=True))
    def get(self, department_id):
        user_id = int(get_jwt_identity())
        return service.list_by_department(user_id=user_id, department_id=department_id)


@blp.route("/control-table")
class StudentControlTableResource(MethodView):
    @roles_required("REITOR", "DIRETOR", "CHEFE", "ADMIN")
    @blp.arguments(StudentControlCreateSchema)
    @blp.response(200, StudentControlResponseSchema)
    def post(self, payload):
        user_id = int(get_jwt_identity())
        return service.create_control_table(
            user_id=user_id,
            department_id=payload["department_id"],
            academic_year_id=payload["academic_year_id"],
        )


@blp.route("/<int:student_id>/status")
class StudentStatusResource(MethodView):
    @roles_required("REITOR", "DIRETOR", "CHEFE", "ADMIN")
    @blp.arguments(StudentStatusUpdateSchema)
    @blp.response(200, StudentStatusResponseSchema)
    def put(self, payload, student_id):
        user_id = int(get_jwt_identity())
        return service.update_status(
            user_id=user_id,
            student_id=student_id,
            academic_year_id=payload["academic_year_id"],
            status=payload["status"],
            academic_level=payload.get("academic_level"),
        )

    @roles_required("REITOR", "DIRETOR", "CHEFE", "ADMIN")
    @blp.arguments(StudentStatusQuerySchema, location="query")
    @blp.response(200, StudentStatusResponseSchema)
    def get(self, query, student_id):
        user_id = int(get_jwt_identity())
        return service.get_status(
            user_id=user_id,
            student_id=student_id,
            academic_year_id=query["academic_year_id"],
        )


@blp.route("/status/by-department/<int:department_id>")
class StudentStatusByDepartmentResource(MethodView):
    @roles_required("REITOR", "DIRETOR", "CHEFE", "ADMIN")
    @blp.arguments(StudentStatusQuerySchema, location="query")
    @blp.response(200, StudentStatusListResponseSchema(many=True))
    def get(self, query, department_id):
        user_id = int(get_jwt_identity())
        return service.list_status_by_department(
            user_id=user_id,
            department_id=department_id,
            academic_year_id=query["academic_year_id"],
        )

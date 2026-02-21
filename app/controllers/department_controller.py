from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint

from app.auth.decorators import roles_required
from app.schemas.department_schema import DepartmentCreateSchema, DepartmentResponseSchema, DepartmentUpdateSchema
from app.services.department_service import DepartmentService


blp = Blueprint("Departments", "departments", url_prefix="/api/departments", description="Departments")
service = DepartmentService()


@blp.route("")
class DepartmentCollectionResource(MethodView):
    @roles_required("ADMIN")
    @blp.arguments(DepartmentCreateSchema)
    @blp.response(201, DepartmentResponseSchema)
    def post(self, payload):
        actor_id = int(get_jwt_identity())
        return service.create(payload, actor_id=actor_id)

    @roles_required("ADMIN")
    @blp.response(200, DepartmentResponseSchema(many=True))
    def get(self):
        return service.list_all()


@blp.route("/by-unit/<int:unit_id>")
class DepartmentByUnitResource(MethodView):
    @roles_required("ADMIN")
    @blp.response(200, DepartmentResponseSchema(many=True))
    def get(self, unit_id):
        return service.list_by_unit(unit_id)


@blp.route("/<int:department_id>")
class DepartmentResource(MethodView):
    @roles_required("ADMIN")
    @blp.response(200, DepartmentResponseSchema)
    def get(self, department_id):
        return service.get_by_id(department_id)

    @roles_required("ADMIN")
    @blp.arguments(DepartmentUpdateSchema)
    @blp.response(200, DepartmentResponseSchema)
    def put(self, payload, department_id):
        actor_id = int(get_jwt_identity())
        return service.update(department_id, payload, actor_id=actor_id)

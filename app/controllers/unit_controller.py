from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint

from app.auth.decorators import roles_required
from app.schemas.unit_schema import UnitCreateSchema, UnitResponseSchema, UnitUpdateSchema
from app.services.unit_service import UnitService


blp = Blueprint("Units", "units", url_prefix="/api/units", description="Organizational units")
service = UnitService()


@blp.route("")
class UnitCollectionResource(MethodView):
    @roles_required("REITOR", "DIRETOR")
    @blp.arguments(UnitCreateSchema)
    @blp.response(201, UnitResponseSchema)
    def post(self, payload):
        actor_id = int(get_jwt_identity())
        return service.create(payload, actor_id=actor_id)

    @roles_required("REITOR", "DIRETOR")
    @blp.response(200, UnitResponseSchema(many=True))
    def get(self):
        return service.list_all()


@blp.route("/<int:unit_id>")
class UnitResource(MethodView):
    @roles_required("REITOR", "DIRETOR")
    @blp.response(200, UnitResponseSchema)
    def get(self, unit_id):
        return service.get_by_id(unit_id)

    @roles_required("REITOR", "DIRETOR")
    @blp.arguments(UnitUpdateSchema)
    @blp.response(200, UnitResponseSchema)
    def put(self, payload, unit_id):
        actor_id = int(get_jwt_identity())
        return service.update(unit_id, payload, actor_id=actor_id)

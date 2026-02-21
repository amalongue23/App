from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint

from app.auth.decorators import roles_required
from app.schemas.dataset_schema import (
    DatasetRunResponseSchema,
    DatasetValidateSchema,
    DatasetValidationResponseSchema,
    UnifySourcesSchema,
)
from app.services.dataset_service import DatasetService


blp = Blueprint("Datasets", "datasets", url_prefix="/api/datasets", description="Data unification and validation")
service = DatasetService()


@blp.route("/unify")
class DatasetUnifyResource(MethodView):
    @roles_required("REITOR")
    @blp.arguments(UnifySourcesSchema)
    @blp.response(200, DatasetRunResponseSchema)
    def post(self, payload):
        actor_id = int(get_jwt_identity())
        return service.unify_and_store(payload["sources"], actor_id=actor_id)


@blp.route("/validate")
class DatasetValidateResource(MethodView):
    @roles_required("REITOR")
    @blp.arguments(DatasetValidateSchema)
    @blp.response(200, DatasetValidationResponseSchema)
    def post(self, payload):
        actor_id = int(get_jwt_identity())
        return {"errors": service.validate_dataset(payload["dataset"], actor_id=actor_id)}

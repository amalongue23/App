from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint

from app.auth.decorators import roles_required
from app.schemas.academic_year_schema import AcademicYearCreateSchema, AcademicYearResponseSchema
from app.services.academic_year_service import AcademicYearService


blp = Blueprint("AcademicYears", "academic_years", url_prefix="/api/academic-years", description="Academic years")
service = AcademicYearService()


@blp.route("")
class AcademicYearCollectionResource(MethodView):
    @roles_required("REITOR")
    @blp.arguments(AcademicYearCreateSchema)
    @blp.response(201, AcademicYearResponseSchema)
    def post(self, payload):
        actor_id = int(get_jwt_identity())
        return service.open_new_year(payload["year_label"], actor_id=actor_id)

    @roles_required("REITOR")
    @blp.response(200, AcademicYearResponseSchema(many=True))
    def get(self):
        return service.list_years()

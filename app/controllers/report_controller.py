from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint

from app.auth.decorators import roles_required
from app.schemas.report_schema import ReportRequestSchema, ReportResponseSchema
from app.services.report_service import ReportService


blp = Blueprint("Reports", "reports", url_prefix="/api/reports", description="Generate reports")
service = ReportService()


@blp.route("/generate")
class ReportGenerateResource(MethodView):
    @roles_required("REITOR", "DIRETOR")
    @blp.arguments(ReportRequestSchema)
    @blp.response(200, ReportResponseSchema)
    def post(self, payload):
        actor_id = int(get_jwt_identity())
        report_type = payload["report_type"]
        rows = service.generate(report_type, payload.get("params", {}), actor_id=actor_id)
        return {"report_type": report_type, "rows": rows}

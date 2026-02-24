from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint
from app.auth.decorators import roles_required
from app.schemas.dashboard_schema import DirectorDashboardStatisticsSchema
from app.services.chief_dashboard_service import DashboardService

blp = Blueprint("Statistics", "statistics", url_prefix="/api/statistics", description="Statistics for director dashboard")
service = DashboardService()

@blp.route("/director")
class DirectorStatisticsResource(MethodView):
    @roles_required("DIRETOR")
    @blp.arguments(DirectorDashboardStatisticsSchema, location="query")
    @blp.response(200, DirectorDashboardStatisticsSchema)
    def get(self, query):
        user_id = int(get_jwt_identity())
        return service.get_director_dashboard_statistics(
            user_id=user_id,
            ano_academico_id=query["ano_academico_id"],
            ano_lectivo=query["ano_lectivo"],
            unit_id=query.get("unit_id"),
            department_id=query.get("department_id"),
            course_id=query.get("course_id"),
            nivel_academico=query.get("nivel_academico"),
            faixa_etaria=query.get("faixa_etaria"),
            sexo=query.get("sexo")
        )

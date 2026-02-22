from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint

from app.auth.decorators import roles_required
from app.schemas.dashboard_schema import (
    AdminDashboardResponseSchema,
    ChiefDashboardQuerySchema,
    ChiefDashboardResponseSchema,
    DirectorDashboardResponseSchema,
    DashboardFiltersResponseSchema,
    RectorDashboardResponseSchema,
)
from app.services.chief_dashboard_service import DashboardService


blp = Blueprint("Dashboard", "dashboard", url_prefix="/api/dashboard", description="Role dashboards")
service = DashboardService()


@blp.route("/filters")
class DashboardFiltersResource(MethodView):
    @roles_required("REITOR", "DIRETOR", "CHEFE", "ADMIN")
    @blp.response(200, DashboardFiltersResponseSchema)
    def get(self):
        user_id = int(get_jwt_identity())
        return service.list_dashboard_filters(user_id=user_id)


@blp.route("/chief")
class ChiefDashboardResource(MethodView):
    @roles_required("CHEFE")
    @blp.arguments(ChiefDashboardQuerySchema, location="query")
    @blp.response(200, ChiefDashboardResponseSchema)
    def get(self, query):
        user_id = int(get_jwt_identity())
        return service.get_chief_dashboard(
            user_id=user_id,
            ano_academico_id=query["ano_academico_id"],
            ano_lectivo=query["ano_lectivo"],
            unit_id=query.get("unit_id"),
            department_id=query.get("department_id"),
            course_id=query.get("course_id"),
        )


@blp.route("/director")
class DirectorDashboardResource(MethodView):
    @roles_required("DIRETOR")
    @blp.arguments(ChiefDashboardQuerySchema, location="query")
    @blp.response(200, DirectorDashboardResponseSchema)
    def get(self, query):
        user_id = int(get_jwt_identity())
        return service.get_director_dashboard(
            user_id=user_id,
            ano_academico_id=query["ano_academico_id"],
            ano_lectivo=query["ano_lectivo"],
            unit_id=query.get("unit_id"),
            department_id=query.get("department_id"),
            course_id=query.get("course_id"),
        )


@blp.route("/reitor")
class RectorDashboardResource(MethodView):
    @roles_required("REITOR", "ADMIN")
    @blp.arguments(ChiefDashboardQuerySchema, location="query")
    @blp.response(200, RectorDashboardResponseSchema)
    def get(self, query):
        user_id = int(get_jwt_identity())
        return service.get_rector_dashboard(
            user_id=user_id,
            ano_academico_id=query["ano_academico_id"],
            ano_lectivo=query["ano_lectivo"],
            unit_id=query.get("unit_id"),
            department_id=query.get("department_id"),
            course_id=query.get("course_id"),
        )


@blp.route("/admin")
class AdminDashboardResource(MethodView):
    @roles_required("ADMIN")
    @blp.response(200, AdminDashboardResponseSchema)
    def get(self):
        user_id = int(get_jwt_identity())
        return service.get_admin_dashboard(user_id=user_id)

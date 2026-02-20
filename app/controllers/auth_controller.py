from flask.views import MethodView
from flask_smorest import Blueprint

from app.services.auth_service import AuthService
from app.schemas.auth_schema import LoginSchema, TokenResponseSchema


blp = Blueprint("Auth", "auth", url_prefix="/api/auth", description="Authentication")
service = AuthService()


@blp.route("/login")
class LoginResource(MethodView):
    @blp.arguments(LoginSchema)
    @blp.response(200, TokenResponseSchema)
    def post(self, payload):
        token = service.login(payload["username"], payload["password"])
        return {"access_token": token}

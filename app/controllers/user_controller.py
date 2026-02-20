from flask.views import MethodView
from flask_smorest import Blueprint

from app.auth.decorators import roles_required
from app.schemas.user_schema import UserCreateSchema, UserResponseSchema
from app.services.auth_service import AuthService
from app.services.user_service import UserService


blp = Blueprint("Users", "users", url_prefix="/api/users", description="Manage users/chiefs")
auth_service = AuthService()
user_service = UserService()


@blp.route("")
class UserCollectionResource(MethodView):
    @roles_required("REITOR", "DIRETOR")
    @blp.arguments(UserCreateSchema)
    @blp.response(201, UserResponseSchema)
    def post(self, payload):
        return auth_service.create_user(**payload)

    @roles_required("REITOR", "DIRETOR")
    @blp.response(200, UserResponseSchema(many=True))
    def get(self):
        return user_service.list_all()

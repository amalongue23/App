from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint

from app.auth.decorators import roles_required
from app.schemas.user_schema import (
    UserActivityQuerySchema,
    UserActivityResponseSchema,
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)
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
        actor_id = int(get_jwt_identity())
        return auth_service.create_user(**payload, actor_id=actor_id)

    @roles_required("REITOR", "DIRETOR")
    @blp.response(200, UserResponseSchema(many=True))
    def get(self):
        return user_service.list_all()


@blp.route("/<int:user_id>")
class UserResource(MethodView):
    @roles_required("REITOR", "DIRETOR")
    @blp.response(200, UserResponseSchema)
    def get(self, user_id):
        return user_service.get_by_id(user_id=user_id)

    @roles_required("ADMIN")
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserResponseSchema)
    def put(self, payload, user_id):
        actor_id = int(get_jwt_identity())
        return user_service.update(user_id=user_id, data=payload, actor_id=actor_id)

    @roles_required("ADMIN")
    @blp.response(200, UserResponseSchema)
    def delete(self, user_id):
        actor_id = int(get_jwt_identity())
        return user_service.deactivate(user_id=user_id, actor_id=actor_id)


@blp.route("/<int:user_id>/activities")
class UserActivityResource(MethodView):
    @roles_required("REITOR", "DIRETOR")
    @blp.arguments(UserActivityQuerySchema, location="query")
    @blp.response(200, UserActivityResponseSchema(many=True))
    def get(self, query, user_id):
        return user_service.list_activities(user_id=user_id, filters=query)

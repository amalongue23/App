from werkzeug.security import generate_password_hash

from flask_smorest import abort

from app.extensions import db
from app.repositories.user_repository import UserRepository
from app.services.user_activity_service import UserActivityService


class UserService:
    def __init__(self):
        self.repository = UserRepository()
        self.activity_service = UserActivityService()

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if not user:
            abort(404, message="User not found")
        return user

    def update(self, user_id: int, data: dict, actor_id: int | None):
        user = self.get_by_id(user_id)

        if "username" in data and data["username"] != user.username:
            duplicate = self.repository.get_by_username_excluding(data["username"], user.id)
            if duplicate:
                abort(409, message="Username already exists")

        payload = dict(data)
        if "password" in payload:
            raw_password = payload.pop("password")
            if raw_password:
                payload["password_hash"] = generate_password_hash(raw_password)

        updated = self.repository.update(user, **payload)
        self.activity_service.log(
            user_id=updated.id,
            actor_id=actor_id,
            action="USER_UPDATED",
            description="Dados do usuário foram atualizados.",
        )
        if actor_id and actor_id != updated.id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="USER_UPDATED",
                description=f"Atualizou o usuário '{updated.username}'.",
            )
        return updated

    def deactivate(self, user_id: int, actor_id: int | None):
        user = self.get_by_id(user_id)
        user.is_active = False
        db.session.commit()
        self.activity_service.log(
            user_id=user.id,
            actor_id=actor_id,
            action="USER_DEACTIVATED",
            description="Usuário foi desativado.",
        )
        if actor_id and actor_id != user.id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="USER_DEACTIVATED",
                description=f"Desativou o usuário '{user.username}'.",
            )
        return user

    def list_activities(self, user_id: int, filters: dict | None = None):
        user = self.get_by_id(user_id)
        payload = filters or {}
        activities = self.activity_service.list_for_user(
            user_id=user_id,
            limit=payload.get("limit") or 200,
            module=payload.get("module"),
            action=payload.get("action"),
            q=payload.get("q"),
            days=payload.get("days"),
        )
        has_created_event = any(item.action == "USER_CREATED" for item in activities)
        if not has_created_event:
            self.activity_service.log(
                user_id=user.id,
                actor_id=None,
                action="USER_CREATED",
                description="Usuário foi cadastrado no sistema.",
            )
            activities = self.activity_service.list_for_user(
                user_id=user_id,
                limit=payload.get("limit") or 200,
                module=payload.get("module"),
                action=payload.get("action"),
                q=payload.get("q"),
                days=payload.get("days"),
            )
        return activities

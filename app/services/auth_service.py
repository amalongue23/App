from werkzeug.security import check_password_hash, generate_password_hash

from flask_jwt_extended import create_access_token
from flask_smorest import abort

from app.extensions import db
from app.models.department import Department
from app.models.user_scope import UserScope
from app.repositories.user_repository import UserRepository
from app.services.user_activity_service import UserActivityService


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.activity_service = UserActivityService()

    def create_user(
        self,
        full_name: str,
        username: str,
        password: str,
        role: str,
        unit_id: int | None = None,
        department_id: int | None = None,
        photo_url: str | None = None,
        birth_date=None,
        sex: str | None = None,
        actor_id: int | None = None,
    ):
        existing = self.user_repository.get_by_username(username)
        if existing:
            abort(409, message="Username already exists")
        normalized_role = "DIRETOR" if role == "DIRECTOR" else role
        scope_unit_id = unit_id
        scope_department_id = department_id

        if normalized_role == "CHEFE":
            if not department_id:
                abort(400, message="department_id is required for CHEFE role")
            department = Department.query.get(department_id)
            if not department:
                abort(404, message="Department not found")
            scope_unit_id = department.unit_id
            scope_department_id = department.id
        elif normalized_role == "DIRETOR":
            if not unit_id:
                abort(400, message="unit_id is required for DIRETOR role")
            scope_department_id = None
        else:
            scope_unit_id = None
            scope_department_id = None

        created = self.user_repository.create(
            full_name=full_name,
            username=username,
            password_hash=generate_password_hash(password),
            role=normalized_role,
            photo_url=photo_url,
            birth_date=birth_date,
            sex=sex,
        )
        if normalized_role in {"CHEFE", "DIRETOR"}:
            db.session.add(
                UserScope(
                    user_id=created.id,
                    unit_id=scope_unit_id,
                    department_id=scope_department_id,
                )
            )
            db.session.commit()
        self.activity_service.log(
            user_id=created.id,
            actor_id=actor_id,
            action="USER_CREATED",
            description="Usuário foi cadastrado no sistema.",
        )
        if actor_id and actor_id != created.id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="USER_CREATED",
                description=f"Cadastrou o usuário '{created.username}'.",
            )
        return created

    def login(self, username: str, password: str) -> str:
        user = self.user_repository.get_by_username(username)
        if not user or not user.is_active:
            abort(401, message="Invalid credentials")

        if not check_password_hash(user.password_hash, password):
            abort(401, message="Invalid credentials")

        self.activity_service.log(
            user_id=user.id,
            actor_id=user.id,
            action="LOGIN",
            description="Login efetuado com sucesso.",
        )

        return create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role, "username": user.username},
        )

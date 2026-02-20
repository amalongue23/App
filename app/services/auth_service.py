from werkzeug.security import check_password_hash, generate_password_hash

from flask_jwt_extended import create_access_token
from flask_smorest import abort

from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def create_user(self, full_name: str, username: str, password: str, role: str):
        existing = self.user_repository.get_by_username(username)
        if existing:
            abort(409, message="Username already exists")

        return self.user_repository.create(
            full_name=full_name,
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
        )

    def login(self, username: str, password: str) -> str:
        user = self.user_repository.get_by_username(username)
        if not user or not user.is_active:
            abort(401, message="Invalid credentials")

        if not check_password_hash(user.password_hash, password):
            abort(401, message="Invalid credentials")

        return create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role, "username": user.username},
        )

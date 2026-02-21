from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username: str):
        return User.query.filter_by(username=username).first()

    def get_by_username_excluding(self, username: str, user_id: int):
        return User.query.filter(User.username == username, User.id != user_id).first()

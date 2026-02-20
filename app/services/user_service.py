from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def list_all(self):
        return self.repository.list_all()

from app.models.student import Student
from app.repositories.base_repository import BaseRepository


class StudentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Student)

    def list_by_department(self, department_id: int):
        return Student.query.filter_by(department_id=department_id).all()

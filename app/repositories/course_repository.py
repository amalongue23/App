from app.models.course import Course
from app.repositories.base_repository import BaseRepository


class CourseRepository(BaseRepository):
    def __init__(self):
        super().__init__(Course)

    def list_by_department(self, department_id: int):
        return Course.query.filter_by(department_id=department_id).all()

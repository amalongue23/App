from flask_smorest import abort

from app.repositories.course_repository import CourseRepository
from app.repositories.department_repository import DepartmentRepository


class CourseService:
    def __init__(self):
        self.repository = CourseRepository()
        self.department_repository = DepartmentRepository()

    def create(self, data: dict):
        if not self.department_repository.get_by_id(data["department_id"]):
            abort(404, message="Department not found")
        return self.repository.create(**data)

    def update(self, course_id: int, data: dict):
        course = self.repository.get_by_id(course_id)
        if not course:
            abort(404, message="Course not found")
        if "department_id" in data and not self.department_repository.get_by_id(data["department_id"]):
            abort(404, message="Department not found")
        return self.repository.update(course, **data)

    def list_by_department(self, department_id: int):
        return self.repository.list_by_department(department_id)

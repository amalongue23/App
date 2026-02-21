from flask_smorest import abort

from app.repositories.course_repository import CourseRepository
from app.repositories.department_repository import DepartmentRepository
from app.services.user_activity_service import UserActivityService


class CourseService:
    def __init__(self):
        self.repository = CourseRepository()
        self.department_repository = DepartmentRepository()
        self.activity_service = UserActivityService()

    def create(self, data: dict, actor_id: int | None = None):
        if not self.department_repository.get_by_id(data["department_id"]):
            abort(404, message="Department not found")
        created = self.repository.create(**data)
        if actor_id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="COURSE_CREATED",
                description=f"Criou curso '{created.name}'.",
            )
        return created

    def update(self, course_id: int, data: dict, actor_id: int | None = None):
        course = self.repository.get_by_id(course_id)
        if not course:
            abort(404, message="Course not found")
        if "department_id" in data and not self.department_repository.get_by_id(data["department_id"]):
            abort(404, message="Department not found")
        updated = self.repository.update(course, **data)
        if actor_id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="COURSE_UPDATED",
                description=f"Atualizou curso '{updated.name}'.",
            )
        return updated

    def list_by_department(self, department_id: int):
        return self.repository.list_by_department(department_id)

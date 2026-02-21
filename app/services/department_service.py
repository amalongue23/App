from flask_smorest import abort

from app.repositories.department_repository import DepartmentRepository
from app.repositories.unit_repository import UnitRepository
from app.services.user_activity_service import UserActivityService


class DepartmentService:
    def __init__(self):
        self.repository = DepartmentRepository()
        self.unit_repository = UnitRepository()
        self.activity_service = UserActivityService()

    def create(self, data: dict, actor_id: int | None = None):
        unit = self.unit_repository.get_by_id(data["unit_id"])
        if not unit:
            abort(404, message="Organizational unit not found")
        created = self.repository.create(**data)
        if actor_id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="DEPARTMENT_CREATED",
                description=f"Criou departamento '{created.name}'.",
            )
        return created

    def list_all(self):
        return self.repository.list_all()

    def list_by_unit(self, unit_id: int):
        return self.repository.list_by_unit(unit_id)

    def get_by_id(self, department_id: int):
        department = self.repository.get_by_id(department_id)
        if not department:
            abort(404, message="Department not found")
        return department

    def update(self, department_id: int, data: dict, actor_id: int | None = None):
        department = self.get_by_id(department_id)
        if "unit_id" in data and not self.unit_repository.get_by_id(data["unit_id"]):
            abort(404, message="Organizational unit not found")
        updated = self.repository.update(department, **data)
        if actor_id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="DEPARTMENT_UPDATED",
                description=f"Atualizou departamento '{updated.name}'.",
            )
        return updated

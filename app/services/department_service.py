from flask_smorest import abort

from app.repositories.department_repository import DepartmentRepository
from app.repositories.unit_repository import UnitRepository


class DepartmentService:
    def __init__(self):
        self.repository = DepartmentRepository()
        self.unit_repository = UnitRepository()

    def create(self, data: dict):
        unit = self.unit_repository.get_by_id(data["unit_id"])
        if not unit:
            abort(404, message="Organizational unit not found")
        return self.repository.create(**data)

    def list_all(self):
        return self.repository.list_all()

    def list_by_unit(self, unit_id: int):
        return self.repository.list_by_unit(unit_id)

    def get_by_id(self, department_id: int):
        department = self.repository.get_by_id(department_id)
        if not department:
            abort(404, message="Department not found")
        return department

    def update(self, department_id: int, data: dict):
        department = self.get_by_id(department_id)
        if "unit_id" in data and not self.unit_repository.get_by_id(data["unit_id"]):
            abort(404, message="Organizational unit not found")
        return self.repository.update(department, **data)

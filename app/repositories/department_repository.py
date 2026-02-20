from app.models.department import Department
from app.repositories.base_repository import BaseRepository


class DepartmentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Department)

    def list_by_unit(self, unit_id: int):
        return Department.query.filter_by(unit_id=unit_id).all()

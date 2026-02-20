from flask_smorest import abort

from app.repositories.unit_repository import UnitRepository


class UnitService:
    def __init__(self):
        self.repository = UnitRepository()

    def create(self, data: dict):
        return self.repository.create(**data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, unit_id: int):
        unit = self.repository.get_by_id(unit_id)
        if not unit:
            abort(404, message="Unit not found")
        return unit

    def update(self, unit_id: int, data: dict):
        unit = self.get_by_id(unit_id)
        return self.repository.update(unit, **data)

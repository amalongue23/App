from flask_smorest import abort

from app.repositories.unit_repository import UnitRepository
from app.services.user_activity_service import UserActivityService


class UnitService:
    def __init__(self):
        self.repository = UnitRepository()
        self.activity_service = UserActivityService()

    def create(self, data: dict, actor_id: int | None = None):
        created = self.repository.create(**data)
        if actor_id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="UNIT_CREATED",
                description=f"Criou unidade orgânica '{created.name}'.",
            )
        return created

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, unit_id: int):
        unit = self.repository.get_by_id(unit_id)
        if not unit:
            abort(404, message="Unit not found")
        return unit

    def update(self, unit_id: int, data: dict, actor_id: int | None = None):
        unit = self.get_by_id(unit_id)
        updated = self.repository.update(unit, **data)
        if actor_id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="UNIT_UPDATED",
                description=f"Atualizou unidade orgânica '{updated.name}'.",
            )
        return updated

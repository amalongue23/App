from app.models.organizational_unit import OrganizationalUnit
from app.repositories.base_repository import BaseRepository


class UnitRepository(BaseRepository):
    def __init__(self):
        super().__init__(OrganizationalUnit)

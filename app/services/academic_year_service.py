from datetime import datetime

from app.repositories.academic_year_repository import AcademicYearRepository
from app.services.user_activity_service import UserActivityService


class AcademicYearService:
    def __init__(self):
        self.repository = AcademicYearRepository()
        self.activity_service = UserActivityService()

    def open_new_year(self, year_label: str, actor_id: int | None = None):
        open_years = self.repository.get_open_years()
        for year in open_years:
            self.repository.update(year, is_open=False, closed_at=datetime.utcnow())
        created = self.repository.create(year_label=year_label, is_open=True)
        if actor_id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="ACADEMIC_YEAR_OPENED",
                description=f"Abriu novo ano acadêmico '{year_label}'.",
            )
        return created

    def list_years(self):
        return self.repository.list_desc()

from app.models.academic_year import AcademicYear
from app.repositories.base_repository import BaseRepository


class AcademicYearRepository(BaseRepository):
    def __init__(self):
        super().__init__(AcademicYear)

    def get_open_years(self):
        return AcademicYear.query.filter_by(is_open=True).all()

    def list_desc(self):
        return AcademicYear.query.order_by(AcademicYear.opened_at.desc()).all()

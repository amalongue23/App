from app.models.academic_year import AcademicYear
from app.repositories.base_repository import BaseRepository


class AcademicYearRepository(BaseRepository):
    def __init__(self):
        super().__init__(AcademicYear)

    def get_open_years(self):
        return AcademicYear.query.filter_by(is_open=True).all()

    def list_desc(self):
        years = AcademicYear.query.all()

        def start_year(item: AcademicYear):
            try:
                return int((item.year_label or "").split("-")[0])
            except (ValueError, TypeError, AttributeError):
                return 0

        return sorted(years, key=start_year, reverse=True)

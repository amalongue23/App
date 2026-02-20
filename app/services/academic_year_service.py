from datetime import datetime

from app.repositories.academic_year_repository import AcademicYearRepository


class AcademicYearService:
    def __init__(self):
        self.repository = AcademicYearRepository()

    def open_new_year(self, year_label: str):
        open_years = self.repository.get_open_years()
        for year in open_years:
            self.repository.update(year, is_open=False, closed_at=datetime.utcnow())
        return self.repository.create(year_label=year_label, is_open=True)

    def list_years(self):
        return self.repository.list_desc()

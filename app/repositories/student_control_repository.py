from app.models.student_control import StudentControl
from app.repositories.base_repository import BaseRepository


class StudentControlRepository(BaseRepository):
    def __init__(self):
        super().__init__(StudentControl)

    def find_by_student_year(self, student_id: int, academic_year_id: int):
        return StudentControl.query.filter_by(
            student_id=student_id,
            academic_year_id=academic_year_id,
        ).first()

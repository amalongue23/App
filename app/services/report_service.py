from app.extensions import db
from app.models.course import Course
from app.models.department import Department
from app.models.organizational_unit import OrganizationalUnit
from app.models.student import Student
from app.services.user_activity_service import UserActivityService


class ReportService:
    def __init__(self):
        self.activity_service = UserActivityService()

    def generate(self, report_type: str, _params: dict, actor_id: int | None = None):
        if report_type == "students_by_department":
            rows = (
                db.session.query(Department.id, Department.name, db.func.count(Student.id))
                .outerjoin(Student, Student.department_id == Department.id)
                .group_by(Department.id, Department.name)
                .all()
            )
            rows = [
                {
                    "department_id": r[0],
                    "department_name": r[1],
                    "students_count": int(r[2]),
                }
                for r in rows
            ]
            if actor_id:
                self.activity_service.log(
                    user_id=actor_id,
                    actor_id=actor_id,
                    action="REPORT_GENERATED",
                    description=f"Gerou relatório '{report_type}'.",
                )
            return rows

        if report_type == "courses_by_department":
            rows = (
                db.session.query(Department.id, Department.name, db.func.count(Course.id))
                .outerjoin(Course, Course.department_id == Department.id)
                .group_by(Department.id, Department.name)
                .all()
            )
            rows = [
                {
                    "department_id": r[0],
                    "department_name": r[1],
                    "courses_count": int(r[2]),
                }
                for r in rows
            ]
            if actor_id:
                self.activity_service.log(
                    user_id=actor_id,
                    actor_id=actor_id,
                    action="REPORT_GENERATED",
                    description=f"Gerou relatório '{report_type}'.",
                )
            return rows

        if report_type == "students_by_unit":
            rows = (
                db.session.query(OrganizationalUnit.id, OrganizationalUnit.name, db.func.count(Student.id))
                .outerjoin(Department, Department.unit_id == OrganizationalUnit.id)
                .outerjoin(Student, Student.department_id == Department.id)
                .group_by(OrganizationalUnit.id, OrganizationalUnit.name)
                .all()
            )
            rows = [
                {
                    "unit_id": r[0],
                    "unit_name": r[1],
                    "students_count": int(r[2]),
                }
                for r in rows
            ]
            if actor_id:
                self.activity_service.log(
                    user_id=actor_id,
                    actor_id=actor_id,
                    action="REPORT_GENERATED",
                    description=f"Gerou relatório '{report_type}'.",
                )
            return rows

        from flask_smorest import abort

        abort(400, message="Unsupported report_type")

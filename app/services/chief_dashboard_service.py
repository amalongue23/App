from collections import defaultdict

from flask_smorest import abort

from app.extensions import db
from app.models.academic_year import AcademicYear
from app.models.activity_log import ActivityLog
from app.models.course import Course
from app.models.course_result import CourseResult
from app.models.department import Department
from app.models.department_notice import DepartmentNotice
from app.models.organizational_unit import OrganizationalUnit
from app.models.professor import Professor
from app.models.student import Student
from app.models.student_control import StudentControl
from app.models.user import User
from app.models.user_scope import UserScope


class DashboardService:
    def _get_user(self, user_id: int):
        user = User.query.get(user_id)
        if not user:
            abort(401, message="Invalid user")
        return user

    def _validate_period(self, ano_academico_id: int, ano_lectivo: str):
        year = AcademicYear.query.get(ano_academico_id)
        if not year:
            abort(404, message="Academic year not found")
        if year.year_label != ano_lectivo:
            abort(400, message="ano_lectivo does not match ano_academico_id")
        return year

    def _base_scope(self, user: User):
        if user.role in {"REITOR", "ADMIN"}:
            unit_ids = [row[0] for row in db.session.query(OrganizationalUnit.id).all()]
            department_ids = [row[0] for row in db.session.query(Department.id).all()]
            course_ids = [row[0] for row in db.session.query(Course.id).all()]
            return {
                "unit_ids": unit_ids,
                "department_ids": department_ids,
                "course_ids": course_ids,
            }

        scope = UserScope.query.filter_by(user_id=user.id).first()
        if user.role == "DIRETOR":
            if not scope or not scope.unit_id:
                abort(404, message="User scope for unit not configured")
            departments = Department.query.filter_by(unit_id=scope.unit_id).all()
            department_ids = [d.id for d in departments]
            course_ids = [row[0] for row in db.session.query(Course.id).filter(Course.department_id.in_(department_ids)).all()] if department_ids else []
            return {
                "unit_ids": [scope.unit_id],
                "department_ids": department_ids,
                "course_ids": course_ids,
            }

        if user.role == "CHEFE":
            if not scope or not scope.department_id:
                abort(404, message="User scope for department not configured")
            department = Department.query.get(scope.department_id)
            if not department:
                abort(404, message="Department not found")
            course_ids = [row[0] for row in db.session.query(Course.id).filter_by(department_id=department.id).all()]
            return {
                "unit_ids": [department.unit_id] if department.unit_id else [],
                "department_ids": [department.id],
                "course_ids": course_ids,
            }

        abort(403, message="Unsupported role for dashboard")

    def _apply_scope_filters(self, base_scope: dict, unit_id=None, department_id=None, course_id=None):
        unit_ids = list(base_scope["unit_ids"])
        department_ids = list(base_scope["department_ids"])
        course_ids = list(base_scope["course_ids"])

        if unit_id is not None:
            if unit_id not in unit_ids:
                abort(403, message="unit_id out of access scope")
            unit_ids = [unit_id]
            department_ids = [row[0] for row in db.session.query(Department.id).filter(Department.unit_id == unit_id).all()]
            course_ids = [row[0] for row in db.session.query(Course.id).filter(Course.department_id.in_(department_ids)).all()] if department_ids else []

        if department_id is not None:
            if department_id not in department_ids:
                abort(403, message="department_id out of access scope")
            department_ids = [department_id]
            dept = Department.query.get(department_id)
            unit_ids = [dept.unit_id] if dept and dept.unit_id else []
            course_ids = [row[0] for row in db.session.query(Course.id).filter(Course.department_id == department_id).all()]

        if course_id is not None:
            if course_id not in course_ids:
                abort(403, message="course_id out of access scope")
            course_ids = [course_id]
            course = Course.query.get(course_id)
            if not course:
                abort(404, message="Course not found")
            department_ids = [course.department_id]
            dept = Department.query.get(course.department_id)
            unit_ids = [dept.unit_id] if dept and dept.unit_id else []

        return {
            "unit_ids": unit_ids,
            "department_ids": department_ids,
            "course_ids": course_ids,
        }

    def list_dashboard_filters(self, user_id: int):
        user = self._get_user(user_id)
        base_scope = self._base_scope(user)

        years = AcademicYear.query.order_by(AcademicYear.opened_at.desc()).all()
        units = (
            OrganizationalUnit.query.filter(OrganizationalUnit.id.in_(base_scope["unit_ids"]))
            .order_by(OrganizationalUnit.name)
            .all()
            if base_scope["unit_ids"]
            else []
        )
        departments = (
            Department.query.filter(Department.id.in_(base_scope["department_ids"]))
            .order_by(Department.name)
            .all()
            if base_scope["department_ids"]
            else []
        )
        courses = (
            Course.query.filter(Course.id.in_(base_scope["course_ids"]))
            .order_by(Course.name)
            .all()
            if base_scope["course_ids"]
            else []
        )

        return {
            "anos": [{"ano_academico_id": year.id, "ano_lectivo": year.year_label} for year in years],
            "units": [{"id": unit.id, "name": unit.name, "code": unit.code} for unit in units],
            "departments": [
                {"id": dep.id, "name": dep.name, "code": dep.code, "unit_id": dep.unit_id}
                for dep in departments
            ],
            "courses": [
                {"id": course.id, "name": course.name, "code": course.code, "department_id": course.department_id}
                for course in courses
            ],
        }

    def _course_filter_condition(self, scope_filter: dict):
        if scope_filter["course_ids"]:
            return Course.id.in_(scope_filter["course_ids"])
        if scope_filter["department_ids"]:
            return Course.department_id.in_(scope_filter["department_ids"])
        return Course.id < 0

    def _performance_for_scope(self, scope_filter: dict, ano_academico_id: int, ano_lectivo: str):
        monthly = defaultdict(lambda: {"approved": 0, "failed": 0})
        query_rows = (
            db.session.query(
                CourseResult.reference_month,
                db.func.sum(CourseResult.approved_count),
                db.func.sum(CourseResult.failed_count),
            )
            .join(Course, Course.id == CourseResult.course_id)
            .filter(
                self._course_filter_condition(scope_filter),
                CourseResult.academic_year_id == ano_academico_id,
                CourseResult.academic_term == ano_lectivo,
            )
            .group_by(CourseResult.reference_month)
            .order_by(CourseResult.reference_month)
            .all()
        )
        for month, approved, failed in query_rows:
            monthly[int(month)]["approved"] = int(approved or 0)
            monthly[int(month)]["failed"] = int(failed or 0)

        performance = [{"month": m, "approved": monthly[m]["approved"], "failed": monthly[m]["failed"]} for m in range(1, 7)]
        trends = [{"month": item["month"], "enrollments": item["approved"] + item["failed"]} for item in performance]
        return performance, trends

    def get_chief_dashboard(
        self,
        user_id: int,
        ano_academico_id: int,
        ano_lectivo: str,
        unit_id=None,
        department_id=None,
        course_id=None,
    ):
        user = self._get_user(user_id)
        if user.role != "CHEFE":
            abort(403, message="Only CHEFE profile can access this dashboard")

        self._validate_period(ano_academico_id, ano_lectivo)
        scope_filter = self._apply_scope_filters(self._base_scope(user), unit_id, department_id, course_id)

        if not scope_filter["department_ids"]:
            abort(404, message="No department scope available")

        department = Department.query.get(scope_filter["department_ids"][0])
        if not department:
            abort(404, message="Department not found")

        student_count = (
            db.session.query(db.func.count(StudentControl.id))
            .join(Student, Student.id == StudentControl.student_id)
            .filter(
                Student.department_id.in_(scope_filter["department_ids"]),
                StudentControl.academic_year_id == ano_academico_id,
                StudentControl.status == "active",
            )
            .scalar()
            or 0
        )

        courses_count = (
            Course.query.filter(Course.id.in_(scope_filter["course_ids"])).count()
            if scope_filter["course_ids"]
            else 0
        )
        professors_count = Professor.query.filter(Professor.department_id.in_(scope_filter["department_ids"])).count()
        units_count = len(scope_filter["unit_ids"])

        performance, trends = self._performance_for_scope(scope_filter, ano_academico_id, ano_lectivo)

        course_rows = (
            db.session.query(
                Course.id,
                Course.name,
                db.func.sum(CourseResult.approved_count),
                db.func.sum(CourseResult.failed_count),
            )
            .join(CourseResult, CourseResult.course_id == Course.id)
            .filter(
                Course.id.in_(scope_filter["course_ids"]),
                CourseResult.academic_year_id == ano_academico_id,
                CourseResult.academic_term == ano_lectivo,
            )
            .group_by(Course.id, Course.name)
            .order_by(Course.name)
            .all()
        )

        courses = []
        for _, name, approved, failed in course_rows:
            approved_v = int(approved or 0)
            failed_v = int(failed or 0)
            total = approved_v + failed_v
            rate = round((approved_v / total) * 100, 1) if total > 0 else 0
            courses.append({"course": name, "approved": approved_v, "failed": failed_v, "approval_rate": rate})

        activities = (
            ActivityLog.query.filter(ActivityLog.department_id.in_(scope_filter["department_ids"]))
            .order_by(ActivityLog.created_at.desc())
            .limit(5)
            .all()
        )
        notices = (
            DepartmentNotice.query.filter(DepartmentNotice.department_id.in_(scope_filter["department_ids"]))
            .order_by(DepartmentNotice.published_at.desc())
            .limit(5)
            .all()
        )

        return {
            "department": {"id": department.id, "name": department.name, "unit_id": department.unit_id},
            "kpis": {
                "students": int(student_count),
                "courses": int(courses_count),
                "professors": int(professors_count),
                "units": int(units_count),
            },
            "performance": performance,
            "trends": trends,
            "courses": courses,
            "activities": [
                {"actor": activity.actor_name, "message": activity.message, "created_at": activity.created_at.isoformat()}
                for activity in activities
            ],
            "notices": [
                {"title": notice.title, "content": notice.content, "published_at": notice.published_at.isoformat()}
                for notice in notices
            ],
        }

    def get_director_dashboard(
        self,
        user_id: int,
        ano_academico_id: int,
        ano_lectivo: str,
        unit_id=None,
        department_id=None,
        course_id=None,
    ):
        user = self._get_user(user_id)
        if user.role != "DIRETOR":
            abort(403, message="Only DIRETOR profile can access this dashboard")

        self._validate_period(ano_academico_id, ano_lectivo)
        scope_filter = self._apply_scope_filters(self._base_scope(user), unit_id, department_id, course_id)
        if not scope_filter["unit_ids"]:
            abort(404, message="No unit scope available")

        unit = OrganizationalUnit.query.get(scope_filter["unit_ids"][0])
        if not unit:
            abort(404, message="Unit not found")

        students = (
            db.session.query(db.func.count(StudentControl.id))
            .join(Student, Student.id == StudentControl.student_id)
            .filter(
                Student.department_id.in_(scope_filter["department_ids"] or [-1]),
                StudentControl.academic_year_id == ano_academico_id,
                StudentControl.status == "active",
            )
            .scalar()
            or 0
        )
        courses_count = Course.query.filter(Course.id.in_(scope_filter["course_ids"] or [-1])).count()
        professors_count = Professor.query.filter(Professor.department_id.in_(scope_filter["department_ids"] or [-1])).count()
        departments_count = len(scope_filter["department_ids"])

        performance, trends = self._performance_for_scope(scope_filter, ano_academico_id, ano_lectivo)

        dep_summary_rows = (
            db.session.query(
                Department.id,
                Department.name,
                db.func.count(db.distinct(Student.id)),
                db.func.count(db.distinct(Course.id)),
            )
            .outerjoin(Student, Student.department_id == Department.id)
            .outerjoin(Course, Course.department_id == Department.id)
            .filter(Department.id.in_(scope_filter["department_ids"] or [-1]))
            .group_by(Department.id, Department.name)
            .all()
        )
        departments = [
            {
                "department_id": row[0],
                "department_name": row[1],
                "students": int(row[2] or 0),
                "courses": int(row[3] or 0),
            }
            for row in dep_summary_rows
        ]

        activities = (
            ActivityLog.query.filter(ActivityLog.department_id.in_(scope_filter["department_ids"] or [-1]))
            .order_by(ActivityLog.created_at.desc())
            .limit(6)
            .all()
        )
        notices = (
            DepartmentNotice.query.filter(DepartmentNotice.department_id.in_(scope_filter["department_ids"] or [-1]))
            .order_by(DepartmentNotice.published_at.desc())
            .limit(6)
            .all()
        )

        return {
            "unit": {"id": unit.id, "name": unit.name, "code": unit.code},
            "kpis": {
                "students": int(students),
                "courses": int(courses_count),
                "professors": int(professors_count),
                "departments": int(departments_count),
            },
            "performance": performance,
            "trends": trends,
            "departments": departments,
            "activities": [
                {"actor": activity.actor_name, "message": activity.message, "created_at": activity.created_at.isoformat()}
                for activity in activities
            ],
            "notices": [
                {"title": notice.title, "content": notice.content, "published_at": notice.published_at.isoformat()}
                for notice in notices
            ],
        }

    def get_rector_dashboard(
        self,
        user_id: int,
        ano_academico_id: int,
        ano_lectivo: str,
        unit_id=None,
        department_id=None,
        course_id=None,
    ):
        user = self._get_user(user_id)
        if user.role not in {"REITOR", "ADMIN"}:
            abort(403, message="Only REITOR profile can access this dashboard")

        self._validate_period(ano_academico_id, ano_lectivo)
        scope_filter = self._apply_scope_filters(self._base_scope(user), unit_id, department_id, course_id)

        students = (
            db.session.query(db.func.count(StudentControl.id))
            .join(Student, Student.id == StudentControl.student_id)
            .filter(
                Student.department_id.in_(scope_filter["department_ids"] or [-1]),
                StudentControl.academic_year_id == ano_academico_id,
                StudentControl.status == "active",
            )
            .scalar()
            or 0
        )
        courses_count = Course.query.filter(Course.id.in_(scope_filter["course_ids"] or [-1])).count()
        departments_count = Department.query.filter(Department.id.in_(scope_filter["department_ids"] or [-1])).count()
        units_count = OrganizationalUnit.query.filter(OrganizationalUnit.id.in_(scope_filter["unit_ids"] or [-1])).count()

        performance, trends = self._performance_for_scope(scope_filter, ano_academico_id, ano_lectivo)

        distribution_rows = (
            db.session.query(OrganizationalUnit.name, db.func.count(Course.id))
            .outerjoin(Department, Department.unit_id == OrganizationalUnit.id)
            .outerjoin(Course, Course.department_id == Department.id)
            .filter(OrganizationalUnit.id.in_(scope_filter["unit_ids"] or [-1]))
            .group_by(OrganizationalUnit.name)
            .all()
        )
        total_courses = sum(int(row[1] or 0) for row in distribution_rows) or 1
        distribution = [
            {"unit": row[0], "courses": int(row[1] or 0), "percentage": round((int(row[1] or 0) / total_courses) * 100, 1)}
            for row in distribution_rows
        ]

        units_rows = (
            db.session.query(
                OrganizationalUnit.id,
                OrganizationalUnit.name,
                db.func.count(db.distinct(Student.id)),
                db.func.count(db.distinct(Course.id)),
            )
            .outerjoin(Department, Department.unit_id == OrganizationalUnit.id)
            .outerjoin(Student, Student.department_id == Department.id)
            .outerjoin(Course, Course.department_id == Department.id)
            .filter(OrganizationalUnit.id.in_(scope_filter["unit_ids"] or [-1]))
            .group_by(OrganizationalUnit.id, OrganizationalUnit.name)
            .all()
        )
        units = [
            {"unit_id": row[0], "unit_name": row[1], "students": int(row[2] or 0), "courses": int(row[3] or 0)}
            for row in units_rows
        ]

        activities = (
            ActivityLog.query.filter(ActivityLog.department_id.in_(scope_filter["department_ids"] or [-1]))
            .order_by(ActivityLog.created_at.desc())
            .limit(8)
            .all()
        )
        notices = (
            DepartmentNotice.query.filter(DepartmentNotice.department_id.in_(scope_filter["department_ids"] or [-1]))
            .order_by(DepartmentNotice.published_at.desc())
            .limit(8)
            .all()
        )

        return {
            "institution": {"name": "MPUNA", "period": ano_lectivo},
            "kpis": {
                "students": int(students),
                "courses": int(courses_count),
                "departments": int(departments_count),
                "units": int(units_count),
            },
            "performance": performance,
            "distribution": distribution,
            "units": units,
            "activities": [
                {"actor": activity.actor_name, "message": activity.message, "created_at": activity.created_at.isoformat()}
                for activity in activities
            ],
            "notices": [
                {"title": notice.title, "content": notice.content, "published_at": notice.published_at.isoformat()}
                for notice in notices
            ],
        }

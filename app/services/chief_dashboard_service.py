def get_director_dashboard_statistics(
        self,
        user_id: int,
        ano_academico_id: int,
        ano_lectivo: str,
        unit_id=None,
        department_id=None,
        course_id=None,
        nivel_academico=None,
        faixa_etaria=None,
        sexo=None,
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
        # Dados agregados para estatísticas
        statistics = self._chief_statistics(scope_filter, ano_academico_id, ano_lectivo)
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
            "statistics": statistics,
        }
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta

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
from app.models.user_activity import UserActivity
from app.models.user_scope import UserScope


class DashboardService:
    ACADEMIC_LEVEL_ORDER = [
        "LICENCIATURA_1",
        "LICENCIATURA_2",
        "LICENCIATURA_3",
        "LICENCIATURA_4",
        "LICENCIATURA_5",
        "MESTRADO_1",
        "MESTRADO_2",
    ]

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

        years = sorted(AcademicYear.query.all(), key=lambda item: self._year_sort_key(item.year_label), reverse=True)
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

    def _year_sort_key(self, year_label: str):
        try:
            return int((year_label or "").split("-")[0])
        except (ValueError, TypeError, AttributeError):
            return 0

    def _level_label(self, code: str):
        if not code:
            return "N/A"
        mapping = {
            "LICENCIATURA_1": "Licenciatura 1",
            "LICENCIATURA_2": "Licenciatura 2",
            "LICENCIATURA_3": "Licenciatura 3",
            "LICENCIATURA_4": "Licenciatura 4",
            "LICENCIATURA_5": "Licenciatura 5",
            "MESTRADO_1": "Mestrado 1",
            "MESTRADO_2": "Mestrado 2",
        }
        return mapping.get(code, str(code).replace("_", " ").title())

    def _chief_statistics(self, scope_filter: dict, ano_academico_id: int, ano_lectivo: str):
        department_ids = scope_filter["department_ids"] or [-1]
        course_ids = scope_filter["course_ids"] or [-1]

        year_rows = (
            db.session.query(
                AcademicYear.year_label,
                db.func.sum(db.case((StudentControl.status == "aprovado", 1), else_=0)),
                db.func.sum(db.case((StudentControl.status == "reprovado", 1), else_=0)),
            )
            .join(StudentControl, StudentControl.academic_year_id == AcademicYear.id)
            .join(Student, Student.id == StudentControl.student_id)
            .filter(Student.department_id.in_(department_ids))
            .group_by(AcademicYear.year_label)
            .all()
        )
        sorted_year_rows = sorted(year_rows, key=lambda row: self._year_sort_key(row[0]))
        year_labels = [row[0] for row in sorted_year_rows]
        year_approval_rate = []
        year_failure_rate = []
        year_status_bars = []
        for label, approved, failed in sorted_year_rows:
            approved_v = int(approved or 0)
            failed_v = int(failed or 0)
            total = approved_v + failed_v
            approved_rate = round((approved_v / total) * 100, 1) if total else 0.0
            failed_rate = round((failed_v / total) * 100, 1) if total else 0.0
            year_approval_rate.append(approved_rate)
            year_failure_rate.append(failed_rate)
            year_status_bars.append({"label": label, "approved": approved_rate, "failed": failed_rate})

        course_rows = (
            db.session.query(
                Course.name,
                db.func.sum(CourseResult.approved_count),
                db.func.sum(CourseResult.failed_count),
            )
            .join(CourseResult, CourseResult.course_id == Course.id)
            .filter(
                Course.id.in_(course_ids),
                CourseResult.academic_year_id == ano_academico_id,
                CourseResult.academic_term == ano_lectivo,
            )
            .group_by(Course.name)
            .order_by(Course.name)
            .all()
        )
        course_rates = []
        for name, approved, failed in course_rows:
            approved_v = int(approved or 0)
            failed_v = int(failed or 0)
            total = approved_v + failed_v
            approved_rate = round((approved_v / total) * 100, 1) if total else 0.0
            failed_rate = round((failed_v / total) * 100, 1) if total else 0.0
            course_rates.append({"name": name, "approved": approved_rate, "failed": failed_rate})

        sex_rows = (
            db.session.query(
                Student.sex,
                StudentControl.status,
                db.func.count(StudentControl.id),
            )
            .join(Student, Student.id == StudentControl.student_id)
            .filter(
                Student.department_id.in_(department_ids),
                StudentControl.academic_year_id == ano_academico_id,
            )
            .group_by(Student.sex, StudentControl.status)
            .all()
        )
        sex_status_counts = {
            "M": {"aprovado": 0, "reprovado": 0, "desistente": 0, "active": 0},
            "F": {"aprovado": 0, "reprovado": 0, "desistente": 0, "active": 0},
        }
        for sex, status, count in sex_rows:
            normalized_sex = "F" if str(sex).upper().startswith("F") else "M"
            sex_status_counts[normalized_sex][status] = int(count or 0)

        male_total = sex_status_counts["M"]["aprovado"] + sex_status_counts["M"]["reprovado"]
        female_total = sex_status_counts["F"]["aprovado"] + sex_status_counts["F"]["reprovado"]
        male_rate = round((sex_status_counts["M"]["aprovado"] / male_total) * 100, 1) if male_total else 0.0
        female_rate = round((sex_status_counts["F"]["aprovado"] / female_total) * 100, 1) if female_total else 0.0

        sex_year_rows = (
            db.session.query(
                AcademicYear.year_label,
                Student.sex,
                db.func.count(StudentControl.id),
            )
            .join(StudentControl, StudentControl.academic_year_id == AcademicYear.id)
            .join(Student, Student.id == StudentControl.student_id)
            .filter(Student.department_id.in_(department_ids))
            .group_by(AcademicYear.year_label, Student.sex)
            .all()
        )
        sex_year_map = defaultdict(lambda: {"M": 0, "F": 0})
        for label, sex, count in sex_year_rows:
            normalized_sex = "F" if str(sex).upper().startswith("F") else "M"
            sex_year_map[label][normalized_sex] += int(count or 0)

        latest_year_labels = sorted(sex_year_map.keys(), key=self._year_sort_key)[-6:]
        sex_status_bars = []
        for label in latest_year_labels:
            m_count = sex_year_map[label]["M"]
            f_count = sex_year_map[label]["F"]
            total = m_count + f_count
            sex_status_bars.append(
                {
                    "label": label,
                    "male": round((m_count / total) * 100, 1) if total else 0.0,
                    "female": round((f_count / total) * 100, 1) if total else 0.0,
                }
            )

        level_rows = (
            db.session.query(
                StudentControl.academic_level,
                db.func.sum(db.case((StudentControl.status == "aprovado", 1), else_=0)),
                db.func.sum(db.case((StudentControl.status == "reprovado", 1), else_=0)),
            )
            .join(Student, Student.id == StudentControl.student_id)
            .filter(
                Student.department_id.in_(department_ids),
                StudentControl.academic_year_id == ano_academico_id,
            )
            .group_by(StudentControl.academic_level)
            .all()
        )
        level_map = {str(level or ""): (int(approved or 0), int(failed or 0)) for level, approved, failed in level_rows}
        level_labels = []
        level_approval_rates = []
        for code in self.ACADEMIC_LEVEL_ORDER:
            if code not in level_map:
                continue
            approved_v, failed_v = level_map[code]
            total = approved_v + failed_v
            level_labels.append(self._level_label(code))
            level_approval_rates.append(round((approved_v / total) * 100, 1) if total else 0.0)

        evasion_course_rows = (
            db.session.query(
                Course.name,
                db.func.sum(db.case((StudentControl.status == "desistente", 1), else_=0)),
                db.func.count(StudentControl.id),
            )
            .join(Student, Student.course_id == Course.id)
            .join(StudentControl, StudentControl.student_id == Student.id)
            .filter(
                Course.id.in_(course_ids),
                StudentControl.academic_year_id == ano_academico_id,
            )
            .group_by(Course.name)
            .order_by(Course.name)
            .all()
        )
        evasion_by_course = []
        for name, dropouts, total in evasion_course_rows:
            total_v = int(total or 0)
            value = round((int(dropouts or 0) / total_v) * 100, 1) if total_v else 0.0
            evasion_by_course.append({"name": name, "value": value})

        evasion_level_rows = (
            db.session.query(
                StudentControl.academic_level,
                db.func.sum(db.case((StudentControl.status == "desistente", 1), else_=0)),
                db.func.count(StudentControl.id),
            )
            .join(Student, Student.id == StudentControl.student_id)
            .filter(
                Student.department_id.in_(department_ids),
                StudentControl.academic_year_id == ano_academico_id,
            )
            .group_by(StudentControl.academic_level)
            .all()
        )
        evasion_level_map = {str(level or ""): (int(dropouts or 0), int(total or 0)) for level, dropouts, total in evasion_level_rows}
        evasion_by_level = []
        for code in self.ACADEMIC_LEVEL_ORDER:
            if code not in evasion_level_map:
                continue
            dropouts_v, total_v = evasion_level_map[code]
            value = round((dropouts_v / total_v) * 100, 1) if total_v else 0.0
            evasion_by_level.append({"name": self._level_label(code), "value": value})

        return {
            "year_labels": year_labels,
            "year_approval_rate": year_approval_rate,
            "year_failure_rate": year_failure_rate,
            "course_rates": course_rates,
            "sex_approval_rate": {"male": male_rate, "female": female_rate},
            "sex_status_bars": sex_status_bars,
            "level_labels": level_labels,
            "level_approval_rates": level_approval_rates,
            "year_status_bars": year_status_bars,
            "evasion_by_course": evasion_by_course,
            "evasion_by_level": evasion_by_level,
        }

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
            "statistics": self._chief_statistics(scope_filter, ano_academico_id, ano_lectivo),
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

    def get_admin_dashboard(self, user_id: int):
        user = self._get_user(user_id)
        if user.role != "ADMIN":
            abort(403, message="Only ADMIN profile can access this dashboard")

        total_users = User.query.count()
        active_profiles = db.session.query(db.func.count(db.func.distinct(User.role))).filter(User.is_active.is_(True)).scalar() or 0
        academic_years = AcademicYear.query.count()

        now = datetime.utcnow()
        day_start = datetime(now.year, now.month, now.day)
        labels = []
        logins = []
        operations = []
        creations = []
        operation_actions = {
            "USER_UPDATED",
            "USER_DEACTIVATED",
            "UNIT_UPDATED",
            "DEPARTMENT_UPDATED",
            "COURSE_UPDATED",
            "STUDENT_UPDATED",
            "STUDENT_STATUS_UPDATED",
            "DATASET_VALIDATED",
            "REPORT_GENERATED",
        }
        creation_actions = {
            "USER_CREATED",
            "UNIT_CREATED",
            "DEPARTMENT_CREATED",
            "COURSE_CREATED",
            "STUDENT_CREATED",
            "STUDENT_CONTROL_TABLE_CREATED",
            "ACADEMIC_YEAR_OPENED",
            "DATASET_UNIFIED",
        }

        for idx in range(6, -1, -1):
            d0 = day_start - timedelta(days=idx)
            d1 = d0 + timedelta(days=1)
            labels.append(d0.strftime("%a")[:3].title())
            day_activities = UserActivity.query.filter(UserActivity.created_at >= d0, UserActivity.created_at < d1).all()
            logins.append(sum(1 for item in day_activities if item.action == "LOGIN"))
            operations.append(sum(1 for item in day_activities if item.action in operation_actions))
            creations.append(sum(1 for item in day_activities if item.action in creation_actions))

        role_rows = db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all()
        role_total = sum(int(row[1]) for row in role_rows) or 1
        role_distribution = [
            {
                "role": row[0],
                "label": self._role_label(row[0]),
                "count": int(row[1]),
                "percentage": round((int(row[1]) / role_total) * 100, 1),
            }
            for row in role_rows
        ]

        recent_rows = UserActivity.query.order_by(UserActivity.created_at.desc()).limit(12).all()
        recent_activities = [
            {
                "actor": (item.actor.username if item.actor else (item.user.username if item.user else "sistema")),
                "message": self._activity_message(item.action, item.description),
                "created_at": item.created_at.isoformat(),
            }
            for item in recent_rows
        ]

        probe_start = time.perf_counter()
        db.session.query(db.func.count(User.id)).scalar()
        api_response_ms = max(1, int((time.perf_counter() - probe_start) * 1000))

        return {
            "kpis": {
                "total_users": int(total_users),
                "active_profiles": int(active_profiles),
                "academic_years": int(academic_years),
                "system_status": "online",
                "logins_total": int(sum(logins)),
                "operations_total": int(sum(operations)),
                "creations_total": int(sum(creations)),
            },
            "series": {
                "labels": labels,
                "logins": logins,
                "operations": operations,
                "creations": creations,
            },
            "role_distribution": role_distribution,
            "recent_activities": recent_activities,
            "technical": {
                "api_response_ms": int(api_response_ms),
                "last_backup_label": "Há 1 dia",
                "app_version": os.getenv("APP_VERSION", "v3.8.2"),
                "system_online": True,
            },
        }

    def _role_label(self, role: str):
        mapping = {
            "ADMIN": "Admin",
            "REITOR": "Reitor",
            "DIRETOR": "Diretor Académico",
            "CHEFE": "Chefe de Departamento",
            "OPERADOR": "Operador",
            "COORDENADOR": "Coordenador",
            "SECRETARIA": "Secretaria",
            "PROFESSOR": "Professor",
            "ASSISTENTE": "Assistente",
        }
        return mapping.get(role, role.title() if role else "-")

    def _activity_message(self, action: str, fallback: str):
        mapping = {
            "LOGIN": "acedeu ao sistema",
            "USER_CREATED": "criou novo utilizador",
            "USER_UPDATED": "atualizou utilizador",
            "USER_DEACTIVATED": "desativou utilizador",
            "COURSE_UPDATED": "atualizou plano curricular",
            "STUDENT_STATUS_UPDATED": "alterou status de estudante",
            "ACADEMIC_YEAR_OPENED": "abriu Ano Académico",
            "REPORT_GENERATED": "gerou relatório",
        }
        return mapping.get(action, fallback or action or "executou uma operação")

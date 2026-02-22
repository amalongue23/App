from app.extensions import db
from app.models.course import Course
from app.models.department import Department
from app.models.student import Student
from app.models.student_control import StudentControl
from app.repositories.academic_year_repository import AcademicYearRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.student_control_repository import StudentControlRepository
from app.repositories.student_repository import StudentRepository
from app.services.user_activity_service import UserActivityService


class StudentService:
    def __init__(self):
        self.repository = StudentRepository()
        self.department_repository = DepartmentRepository()
        self.control_repository = StudentControlRepository()
        self.academic_year_repository = AcademicYearRepository()
        self.activity_service = UserActivityService()

    def create(self, user_id: int, data: dict):
        self._enforce_write_permission(user_id=user_id)
        if not self.department_repository.get_by_id(data["department_id"]):
            from flask_smorest import abort

            abort(404, message="Department not found")
        self._enforce_scope(user_id=user_id, department_id=data["department_id"])
        self._ensure_course(data.get("course_id"), data["department_id"])
        created = self.repository.create(**data)
        self.activity_service.log(
            user_id=user_id,
            actor_id=user_id,
            action="STUDENT_CREATED",
            description=f"Cadastrou estudante '{created.full_name}'.",
        )
        return created

    def update(self, user_id: int, student_id: int, data: dict):
        self._enforce_write_permission(user_id=user_id)
        student = self.repository.get_by_id(student_id)
        if not student:
            from flask_smorest import abort

            abort(404, message="Student not found")
        self._enforce_scope(user_id=user_id, department_id=student.department_id)
        if "department_id" in data and not self.department_repository.get_by_id(data["department_id"]):
            from flask_smorest import abort

            abort(404, message="Department not found")
        if "department_id" in data:
            self._enforce_scope(user_id=user_id, department_id=data["department_id"])
        department_id = data.get("department_id", student.department_id)
        if "course_id" in data:
            self._ensure_course(data.get("course_id"), department_id)
        updated = self.repository.update(student, **data)
        self.activity_service.log(
            user_id=user_id,
            actor_id=user_id,
            action="STUDENT_UPDATED",
            description=f"Atualizou estudante '{updated.full_name}'.",
        )
        return updated

    def get_by_id(self, user_id: int, student_id: int):
        student = self.repository.get_by_id(student_id)
        if not student:
            from flask_smorest import abort

            abort(404, message="Student not found")
        self._enforce_scope(user_id=user_id, department_id=student.department_id)
        return student

    def list_by_department(self, user_id: int, department_id: int):
        self._enforce_scope(user_id=user_id, department_id=department_id)
        return self.repository.list_by_department(department_id)

    def create_control_table(self, user_id: int, department_id: int, academic_year_id: int):
        self._enforce_write_permission(user_id=user_id)
        students = self.repository.list_by_department(department_id)
        year = self.academic_year_repository.get_by_id(academic_year_id)
        if not year:
            from flask_smorest import abort

            abort(404, message="Academic year not found")
        self._enforce_scope(user_id=user_id, department_id=department_id)

        created = 0
        for student in students:
            existing = self.control_repository.find_by_student_year(student.id, academic_year_id)
            if existing:
                continue
            self.control_repository.create(
                student_id=student.id,
                academic_year_id=academic_year_id,
                status="active",
                academic_level=student.academic_level,
            )
            created += 1

        self.activity_service.log(
            user_id=user_id,
            actor_id=user_id,
            action="STUDENT_CONTROL_TABLE_CREATED",
            description=f"Criou tabela de controlo para departamento {department_id} no ano {academic_year_id}.",
        )

        return {
            "department_id": department_id,
            "academic_year_id": academic_year_id,
            "created_records": created,
            "total_students": len(students),
        }

    def update_status(self, user_id: int, student_id: int, academic_year_id: int, status: str, academic_level: str | None = None):
        from flask_smorest import abort

        self._enforce_write_permission(user_id=user_id)

        allowed_status = {"active", "aprovado", "reprovado", "desistente"}
        if status not in allowed_status:
            abort(400, message="Invalid status. Use: aprovado, reprovado, desistente, active.")

        student = self.repository.get_by_id(student_id)
        if not student:
            abort(404, message="Student not found")

        year = self.academic_year_repository.get_by_id(academic_year_id)
        if not year:
            abort(404, message="Academic year not found")

        self._enforce_scope(user_id=user_id, department_id=student.department_id)

        control = self.control_repository.find_by_student_year(student_id, academic_year_id)
        current_level = control.academic_level if control else student.academic_level
        target_level = academic_level or current_level

        if target_level and target_level != current_level:
            prev_year = self._get_previous_academic_year(year)
            if prev_year:
                prev_control = self.control_repository.find_by_student_year(student_id, prev_year.id)
                prev_status = prev_control.status if prev_control else None
                if prev_status in {"reprovado", "desistente"}:
                    abort(
                        400,
                        message=(
                            f"Não é permitido alterar ano de frequência para {year.year_label}: "
                            f"no ano anterior ({prev_year.year_label}) o estudante está '{prev_status}'."
                        ),
                    )

        if not control:
            control = self.control_repository.create(
                student_id=student_id,
                academic_year_id=academic_year_id,
                status=status,
                academic_level=target_level,
            )
            if target_level and student.academic_level != target_level:
                self.repository.update(student, academic_level=target_level)
            self.activity_service.log(
                user_id=user_id,
                actor_id=user_id,
                action="STUDENT_STATUS_UPDATED",
                description=(
                    f"Definiu status '{status}' para estudante {student.registration_number} "
                    f"no ano {year.year_label} (nível: {target_level or '-'})"
                ),
            )
            return control
        updated = self.control_repository.update(control, status=status, academic_level=target_level)
        if target_level and student.academic_level != target_level:
            self.repository.update(student, academic_level=target_level)
        self.activity_service.log(
            user_id=user_id,
            actor_id=user_id,
            action="STUDENT_STATUS_UPDATED",
            description=(
                f"Alterou status para '{status}' do estudante {student.registration_number} "
                f"no ano {year.year_label} (nível: {target_level or '-'})"
            ),
        )
        return updated

    def get_status(self, user_id: int, student_id: int, academic_year_id: int):
        from flask_smorest import abort

        student = self.repository.get_by_id(student_id)
        if not student:
            abort(404, message="Student not found")

        year = self.academic_year_repository.get_by_id(academic_year_id)
        if not year:
            abort(404, message="Academic year not found")

        self._enforce_scope(user_id=user_id, department_id=student.department_id)

        control = self.control_repository.find_by_student_year(student_id, academic_year_id)
        if not control:
            return {
                "student_id": student_id,
                "academic_year_id": academic_year_id,
                "status": "nao_definido",
                "academic_level": student.academic_level,
                "updated_at": None,
            }

        return {
            "student_id": student_id,
            "academic_year_id": academic_year_id,
            "status": control.status,
            "academic_level": control.academic_level or student.academic_level,
            "updated_at": control.updated_at,
        }

    def list_status_by_department(self, user_id: int, department_id: int, academic_year_id: int):
        from flask_smorest import abort

        department = self.department_repository.get_by_id(department_id)
        if not department:
            abort(404, message="Department not found")

        year = self.academic_year_repository.get_by_id(academic_year_id)
        if not year:
            abort(404, message="Academic year not found")

        self._enforce_scope(user_id=user_id, department_id=department_id)

        controls = (
            db.session.query(Student.id, StudentControl.status, StudentControl.academic_level)
            .outerjoin(
                StudentControl,
                db.and_(
                    StudentControl.student_id == Student.id,
                    StudentControl.academic_year_id == academic_year_id,
                ),
            )
            .filter(Student.department_id == department_id)
            .all()
        )
        status_map = {row[0]: {"status": row[1], "academic_level": row[2]} for row in controls}

        students = self.repository.list_by_department(department_id)
        return [
            {
                "student_id": student.id,
                "status": (status_map.get(student.id) or {}).get("status") or "nao_definido",
                "academic_level": (status_map.get(student.id) or {}).get("academic_level") or student.academic_level,
            }
            for student in students
        ]

    def _get_previous_academic_year(self, year):
        years = self.academic_year_repository.list_desc()

        def year_start(value: str):
            try:
                return int((value or "").split("-")[0])
            except Exception:
                return -1

        current_start = year_start(year.year_label)
        candidates = [item for item in years if year_start(item.year_label) < current_start]
        if not candidates:
            return None
        return max(candidates, key=lambda item: year_start(item.year_label))

    def _ensure_course(self, course_id: int | None, department_id: int):
        from flask_smorest import abort

        if course_id is None:
            return
        course = Course.query.get(course_id)
        if not course:
            abort(404, message="Course not found")
        if course.department_id != department_id:
            abort(400, message="Course does not belong to the department")

    def _enforce_write_permission(self, user_id: int):
        from flask_smorest import abort
        from app.models.user import User

        user = User.query.get(user_id)
        if not user:
            abort(401, message="Invalid user")
        if user.role not in {"CHEFE", "ADMIN"}:
            abort(403, message="Role not allowed to modify student data")

    def _enforce_scope(self, user_id: int, department_id: int):
        from flask_smorest import abort
        from app.models.department import Department
        from app.models.user import User
        from app.models.user_scope import UserScope

        user = User.query.get(user_id)
        if not user:
            abort(401, message="Invalid user")

        if user.role in {"DIRETOR", "CHEFE"}:
            scope = UserScope.query.filter_by(user_id=user.id).first()
            if not scope:
                abort(403, message="User scope not configured")

            department = Department.query.get(department_id)
            if not department:
                abort(404, message="Department not found")

            if user.role == "CHEFE":
                if scope.department_id != department_id:
                    abort(403, message="Student out of department scope")
            else:
                if scope.unit_id != department.unit_id:
                    abort(403, message="Student out of unit scope")

    def students_count_by_department(self):
        rows = (
            db.session.query(Department.id, Department.name, db.func.count(Student.id))
            .outerjoin(Student, Student.department_id == Department.id)
            .group_by(Department.id, Department.name)
            .all()
        )
        return [
            {
                "department_id": row[0],
                "department_name": row[1],
                "students_count": int(row[2]),
            }
            for row in rows
        ]

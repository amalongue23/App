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

    def update_status(self, user_id: int, student_id: int, academic_year_id: int, status: str):
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
        if not control:
            control = self.control_repository.create(
                student_id=student_id,
                academic_year_id=academic_year_id,
                status=status,
            )
            self.activity_service.log(
                user_id=user_id,
                actor_id=user_id,
                action="STUDENT_STATUS_UPDATED",
                description=f"Definiu status '{status}' para estudante {student.registration_number} no ano {year.year_label}.",
            )
            return control
        updated = self.control_repository.update(control, status=status)
        self.activity_service.log(
            user_id=user_id,
            actor_id=user_id,
            action="STUDENT_STATUS_UPDATED",
            description=f"Alterou status para '{status}' do estudante {student.registration_number} no ano {year.year_label}.",
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
                "updated_at": None,
            }

        return control

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
            db.session.query(Student.id, StudentControl.status)
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
        status_map = {row[0]: row[1] for row in controls}

        students = self.repository.list_by_department(department_id)
        return [
            {"student_id": student.id, "status": status_map.get(student.id) or "nao_definido"}
            for student in students
        ]

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

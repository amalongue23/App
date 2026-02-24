import argparse
from datetime import date, datetime
from random import Random

from werkzeug.security import generate_password_hash

from app import create_app
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

DEFAULT_PASSWORD = "123456"
RAND = Random(42)
DEFAULT_STUDENTS_PER_DEPARTMENT = 60

YEARS = [
    "2017-2018",
    "2018-2019",
    "2019-2020",
    "2020-2021",
    "2021-2022",
    "2022-2023",
    "2023-2024",
    "2024-2025",
    "2025-2026",
]
ACADEMIC_LEVELS = [
    "LICENCIATURA_1",
    "LICENCIATURA_2",
    "LICENCIATURA_3",
    "LICENCIATURA_4",
    "LICENCIATURA_5",
    "MESTRADO_1",
    "MESTRADO_2",
]

SEED_STRUCTURE = [
    {
        "unit": {"name": "Faculdade de Engenharia", "code": "UO-ENG", "description": "Unidade de Engenharia"},
        "director": {"full_name": "Diretor Engenharia", "username": "dir.eng", "role": "DIRETOR"},
        "departments": [
            {
                "name": "Departamento de Computação",
                "code": "DEP-COMP",
                "chief": {"full_name": "Chefe Computação", "username": "chef.comp", "role": "CHEFE"},
                "courses": [
                    {"name": "Engenharia de Software", "code": "CUR-ESW", "credits": 5},
                    {"name": "Sistemas Distribuídos", "code": "CUR-SDI", "credits": 4},
                    {"name": "Inteligência Artificial", "code": "CUR-IAR", "credits": 4},
                ],
            },
            {
                "name": "Departamento de Civil",
                "code": "DEP-CIV",
                "chief": {"full_name": "Chefe Civil", "username": "chef.civ", "role": "CHEFE"},
                "courses": [
                    {"name": "Estruturas", "code": "CUR-EST", "credits": 5},
                    {"name": "Hidráulica", "code": "CUR-HID", "credits": 4},
                    {"name": "Geotecnia", "code": "CUR-GEO", "credits": 4},
                ],
            },
        ],
    },
    {
        "unit": {"name": "Faculdade de Ciências", "code": "UO-CIE", "description": "Unidade de Ciências"},
        "director": {"full_name": "Diretor Ciências", "username": "dir.cie", "role": "DIRETOR"},
        "departments": [
            {
                "name": "Departamento de Matemática",
                "code": "DEP-MAT",
                "chief": {"full_name": "Chefe Matemática", "username": "chef.mat", "role": "CHEFE"},
                "courses": [
                    {"name": "Álgebra Linear", "code": "CUR-ALG", "credits": 4},
                    {"name": "Cálculo Avançado", "code": "CUR-CAL", "credits": 5},
                    {"name": "Probabilidade", "code": "CUR-PRO", "credits": 4},
                ],
            },
            {
                "name": "Departamento de Física",
                "code": "DEP-FIS",
                "chief": {"full_name": "Chefe Física", "username": "chef.fis", "role": "CHEFE"},
                "courses": [
                    {"name": "Mecânica Clássica", "code": "CUR-MEC", "credits": 5},
                    {"name": "Eletromagnetismo", "code": "CUR-ELE", "credits": 4},
                    {"name": "Física Moderna", "code": "CUR-FMD", "credits": 4},
                ],
            },
        ],
    },
    {
        "unit": {"name": "Faculdade de Saúde", "code": "UO-SAU", "description": "Unidade de Saúde"},
        "director": {"full_name": "Diretor Saúde", "username": "dir.sau", "role": "DIRETOR"},
        "departments": [
            {
                "name": "Departamento de Enfermagem",
                "code": "DEP-ENF",
                "chief": {"full_name": "Chefe Enfermagem", "username": "chef.enf", "role": "CHEFE"},
                "courses": [
                    {"name": "Cuidados Intensivos", "code": "CUR-CIN", "credits": 5},
                    {"name": "Saúde Pública", "code": "CUR-SPB", "credits": 4},
                    {"name": "Urgência e Emergência", "code": "CUR-UEM", "credits": 4},
                ],
            },
            {
                "name": "Departamento de Nutrição",
                "code": "DEP-NUT",
                "chief": {"full_name": "Chefe Nutrição", "username": "chef.nut", "role": "CHEFE"},
                "courses": [
                    {"name": "Nutrição Clínica", "code": "CUR-NCL", "credits": 4},
                    {"name": "Dietoterapia", "code": "CUR-DIE", "credits": 4},
                    {"name": "Avaliação Nutricional", "code": "CUR-ANU", "credits": 4},
                ],
            },
        ],
    },
]

ADMIN_USERS = [
    {"full_name": "Administrador Geral", "username": "admin.master", "role": "ADMIN"},
    {"full_name": "Administrador Operações", "username": "admin.ops", "role": "ADMIN"},
]


def get_or_create_academic_year(label: str) -> AcademicYear:
    year = AcademicYear.query.filter_by(year_label=label).first()
    if year:
        return year

    year = AcademicYear(year_label=label, is_open=(label == YEARS[-1]))
    db.session.add(year)
    db.session.flush()
    return year


def get_or_create_user(user_data: dict) -> User:
    user = User.query.filter_by(username=user_data["username"]).first()
    if user:
        return user

    user = User(
        full_name=user_data["full_name"],
        username=user_data["username"],
        password_hash=generate_password_hash(DEFAULT_PASSWORD),
        role=user_data["role"],
        is_active=True,
    )
    db.session.add(user)
    db.session.flush()
    return user


def get_or_create_scope(user_id: int, unit_id: int | None, department_id: int | None):
    scope = UserScope.query.filter_by(user_id=user_id).first()
    if scope:
        scope.unit_id = unit_id
        scope.department_id = department_id
        return

    db.session.add(UserScope(user_id=user_id, unit_id=unit_id, department_id=department_id))


def get_or_create_unit(unit_data: dict) -> OrganizationalUnit:
    unit = OrganizationalUnit.query.filter_by(code=unit_data["code"]).first()
    if unit:
        return unit

    unit = OrganizationalUnit(**unit_data)
    db.session.add(unit)
    db.session.flush()
    return unit


def get_or_create_department(unit_id: int, dep_data: dict) -> Department:
    department = Department.query.filter_by(code=dep_data["code"]).first()
    if department:
        return department

    department = Department(name=dep_data["name"], code=dep_data["code"], unit_id=unit_id)
    db.session.add(department)
    db.session.flush()
    return department


def get_or_create_course(department_id: int, course_data: dict) -> Course:
    course = Course.query.filter_by(code=course_data["code"]).first()
    if course:
        return course

    course = Course(
        name=course_data["name"],
        code=course_data["code"],
        department_id=department_id,
        credits=course_data["credits"],
    )
    db.session.add(course)
    db.session.flush()
    return course


def ensure_professors(department: Department):
    existing = Professor.query.filter_by(department_id=department.id).count()
    needed = max(4, len(department.courses) * 2)
    for idx in range(existing + 1, needed + 1):
        db.session.add(
            Professor(
                full_name=f"Professor {department.code}-{idx}",
                department_id=department.id,
            )
        )


def ensure_students(department: Department, count: int = 60):
    existing = Student.query.filter_by(department_id=department.id).count()
    courses = Course.query.filter_by(department_id=department.id).all()
    for idx in range(existing + 1, count + 1):
        reg = f"{department.code}-STD-{idx:03d}"
        student = Student.query.filter_by(registration_number=reg).first()
        if student:
            continue
        course_id = courses[(idx - 1) % len(courses)].id if courses else None
        db.session.add(
            Student(
                full_name=f"Aluno {department.code} {idx}",
                registration_number=reg,
                email=f"{department.code.lower()}.std{idx}@gmail.com",
                department_id=department.id,
                course_id=course_id,
                birth_date=date(2000 + (idx % 5), ((idx % 12) + 1), ((idx % 28) + 1)),
                sex="M" if idx % 2 == 0 else "F",
                academic_level=ACADEMIC_LEVELS[(idx - 1) % len(ACADEMIC_LEVELS)],
            )
        )


def _status_for(student_id: int, year: AcademicYear, latest_year_id: int) -> str:
    key = (student_id * 31 + year.id * 17) % 100
    if year.id == latest_year_id:
        if key < 70:
            return "active"
        if key < 90:
            return "aprovado"
        if key < 97:
            return "reprovado"
        return "desistente"
    if key < 70:
        return "aprovado"
    if key < 90:
        return "reprovado"
    return "desistente"


def ensure_student_controls(department: Department, years: list[AcademicYear]):
    students = Student.query.filter_by(department_id=department.id).all()
    latest_year_id = max((year.id for year in years), default=0)
    for year in years:
        for student in students:
            status = _status_for(student.id, year, latest_year_id)
            control = StudentControl.query.filter_by(student_id=student.id, academic_year_id=year.id).first()
            if control:
                control.status = status
                control.academic_level = student.academic_level
                control.updated_at = datetime.utcnow()
                continue
            db.session.add(
                StudentControl(
                    student_id=student.id,
                    academic_year_id=year.id,
                    status=status,
                    academic_level=student.academic_level,
                    updated_at=datetime.utcnow(),
                )
            )


def ensure_course_results(department: Department, years: list[AcademicYear]):
    courses = Course.query.filter_by(department_id=department.id).all()
    for year in years:
        term = year.year_label
        for course in courses:
            for month in range(1, 13):
                result = CourseResult.query.filter_by(
                    course_id=course.id,
                    academic_year_id=year.id,
                    academic_term=term,
                    reference_month=month,
                ).first()
                if result:
                    continue

                base = 15 + (course.id % 7) + month
                approved = base + RAND.randint(5, 25)
                failed = max(3, int(approved * (0.15 + RAND.random() * 0.2)))
                db.session.add(
                    CourseResult(
                        course_id=course.id,
                        academic_year_id=year.id,
                        academic_term=term,
                        reference_month=month,
                        approved_count=approved,
                        failed_count=failed,
                    )
                )


def ensure_activity_logs(department: Department):
    if ActivityLog.query.filter_by(department_id=department.id).count() >= 5:
        return

    samples = [
        "Criou novo plano curricular do curso.",
        "Atualizou carga horária de disciplina.",
        "Aprovou proposta de seminário científico.",
        "Reunião com docentes concluída.",
        "Publicou calendário de avaliações.",
    ]
    for idx, msg in enumerate(samples, start=1):
        db.session.add(
            ActivityLog(
                department_id=department.id,
                actor_name=f"Gestor {department.code}",
                message=msg,
                created_at=datetime.utcnow(),
            )
        )


def ensure_notices(department: Department):
    if DepartmentNotice.query.filter_by(department_id=department.id).count() >= 3:
        return

    notices = [
        ("Visita de Inspeção", "Auditoria interna marcada para a próxima semana."),
        ("Falha Elétrica Corrigida", "O problema elétrico no bloco principal foi resolvido."),
        ("Atualização de Matrículas", "Prazo para revisão de matrículas prorrogado."),
    ]
    for title, content in notices:
        db.session.add(
            DepartmentNotice(
                department_id=department.id,
                title=title,
                content=content,
                published_at=datetime.utcnow(),
            )
        )


def seed(students_per_department: int = DEFAULT_STUDENTS_PER_DEPARTMENT) -> None:
    app = create_app()
    with app.app_context():
        years = [get_or_create_academic_year(y) for y in YEARS]
        latest_label = YEARS[-1]
        for year in AcademicYear.query.all():
            year.is_open = year.year_label == latest_label

        for admin in ADMIN_USERS:
            get_or_create_user(admin)

        for entry in SEED_STRUCTURE:
            unit = get_or_create_unit(entry["unit"])

            director = get_or_create_user(entry["director"])
            get_or_create_scope(director.id, unit.id, None)

            for dep in entry["departments"]:
                department = get_or_create_department(unit.id, dep)

                chief = get_or_create_user(dep["chief"])
                get_or_create_scope(chief.id, unit.id, department.id)

                for course in dep["courses"]:
                    get_or_create_course(department.id, course)

                db.session.flush()
                ensure_professors(department)
                ensure_students(department, count=students_per_department)
                db.session.flush()
                ensure_student_controls(department, years)
                ensure_course_results(department, years)
                ensure_activity_logs(department)
                ensure_notices(department)

        db.session.commit()

        print("SEED_OK")
        print("default_password=123456")
        print(f"students_per_department={students_per_department}")


def _parse_args():
    parser = argparse.ArgumentParser(description="Seed de dados demo MPUNA/Unistats")
    parser.add_argument(
        "--students-per-department",
        type=int,
        default=DEFAULT_STUDENTS_PER_DEPARTMENT,
        help=f"Quantidade de estudantes por departamento (default: {DEFAULT_STUDENTS_PER_DEPARTMENT})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    seed(students_per_department=max(1, int(args.students_per_department)))

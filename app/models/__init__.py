from app.models.academic_year import AcademicYear
from app.models.activity_log import ActivityLog
from app.models.course import Course
from app.models.course_result import CourseResult
from app.models.dataset_run import DatasetRun
from app.models.department import Department
from app.models.department_notice import DepartmentNotice
from app.models.organizational_unit import OrganizationalUnit
from app.models.professor import Professor
from app.models.student import Student
from app.models.student_control import StudentControl
from app.models.user import User
from app.models.user_activity import UserActivity
from app.models.user_scope import UserScope

__all__ = [
    "AcademicYear",
    "OrganizationalUnit",
    "Department",
    "Course",
    "Student",
    "StudentControl",
    "User",
    "UserActivity",
    "DatasetRun",
    "UserScope",
    "CourseResult",
    "ActivityLog",
    "DepartmentNotice",
    "Professor",
]

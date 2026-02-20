from datetime import datetime

from app.extensions import db


class CourseResult(db.Model):
    __tablename__ = "course_results"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey("academic_years.id"), nullable=False)
    academic_term = db.Column(db.String(20), nullable=False)
    reference_month = db.Column(db.Integer, nullable=False)
    approved_count = db.Column(db.Integer, nullable=False, default=0)
    failed_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    course = db.relationship("Course")
    academic_year = db.relationship("AcademicYear")

    __table_args__ = (
        db.UniqueConstraint(
            "course_id",
            "academic_year_id",
            "academic_term",
            "reference_month",
            name="uq_course_result_period",
        ),
    )

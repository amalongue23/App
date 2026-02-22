from datetime import datetime

from app.extensions import db


class StudentControl(db.Model):
    __tablename__ = "student_controls"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey("academic_years.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="active")
    academic_level = db.Column(db.String(40), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship("Student", back_populates="controls")
    academic_year = db.relationship("AcademicYear")

    __table_args__ = (
        db.UniqueConstraint("student_id", "academic_year_id", name="uq_student_academic_year"),
    )

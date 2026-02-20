from datetime import datetime

from app.extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey("organizational_units.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    unit = db.relationship("OrganizationalUnit", back_populates="departments")
    courses = db.relationship("Course", back_populates="department", cascade="all, delete-orphan")
    students = db.relationship("Student", back_populates="department", cascade="all, delete-orphan")

from datetime import datetime

from app.extensions import db


class DepartmentNotice(db.Model):
    __tablename__ = "department_notices"

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    published_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    department = db.relationship("Department")

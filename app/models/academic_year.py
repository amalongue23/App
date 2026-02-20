from datetime import datetime

from app.extensions import db


class AcademicYear(db.Model):
    __tablename__ = "academic_years"

    id = db.Column(db.Integer, primary_key=True)
    year_label = db.Column(db.String(20), unique=True, nullable=False)
    is_open = db.Column(db.Boolean, nullable=False, default=True)
    opened_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

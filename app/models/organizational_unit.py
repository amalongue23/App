from datetime import datetime

from app.extensions import db


class OrganizationalUnit(db.Model):
    __tablename__ = "organizational_units"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    departments = db.relationship("Department", back_populates="unit", cascade="all, delete-orphan")

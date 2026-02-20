from datetime import datetime

from app.extensions import db


class UserScope(db.Model):
    __tablename__ = "user_scopes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    unit_id = db.Column(db.Integer, db.ForeignKey("organizational_units.id"), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User")
    unit = db.relationship("OrganizationalUnit")
    department = db.relationship("Department")

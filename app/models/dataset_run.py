from datetime import datetime

from app.extensions import db


class DatasetRun(db.Model):
    __tablename__ = "dataset_runs"

    id = db.Column(db.Integer, primary_key=True)
    source_count = db.Column(db.Integer, nullable=False, default=0)
    consolidated_data = db.Column(db.JSON, nullable=False)
    validation_errors = db.Column(db.JSON, nullable=False, default=list)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

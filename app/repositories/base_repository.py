from app.extensions import db


class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_by_id(self, record_id: int):
        return self.model.query.get(record_id)

    def list_all(self):
        return self.model.query.all()

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.session.commit()
        return instance

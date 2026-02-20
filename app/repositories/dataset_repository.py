from app.models.dataset_run import DatasetRun
from app.repositories.base_repository import BaseRepository


class DatasetRepository(BaseRepository):
    def __init__(self):
        super().__init__(DatasetRun)

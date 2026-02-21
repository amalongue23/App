from typing import Any

from app.repositories.dataset_repository import DatasetRepository
from app.services.user_activity_service import UserActivityService


class DatasetService:
    def __init__(self):
        self.repository = DatasetRepository()
        self.activity_service = UserActivityService()

    def unify_sources(self, sources: list[list[dict[str, Any]]]):
        consolidated = {}

        for source_index, source_rows in enumerate(sources):
            for row_index, row in enumerate(source_rows):
                if not isinstance(row, dict):
                    continue

                key = (
                    str(row.get("id"))
                    if row.get("id") is not None
                    else row.get("registration_number")
                    or f"source-{source_index}-row-{row_index}"
                )

                if key not in consolidated:
                    consolidated[key] = row.copy()
                else:
                    current = consolidated[key]
                    for k, v in row.items():
                        if v not in (None, ""):
                            current[k] = v

        return list(consolidated.values())

    def validate_dataset(self, dataset: list[dict[str, Any]], actor_id: int | None = None):
        errors = []
        seen_ids = set()

        for idx, row in enumerate(dataset):
            if not isinstance(row, dict):
                errors.append({"index": idx, "error": "row is not an object"})
                continue

            if "name" not in row and "full_name" not in row:
                errors.append({"index": idx, "error": "missing name/full_name"})

            identifier = row.get("id") or row.get("registration_number")
            if not identifier:
                errors.append({"index": idx, "error": "missing id/registration_number"})
            elif identifier in seen_ids:
                errors.append({"index": idx, "error": "duplicate identifier"})
            else:
                seen_ids.add(identifier)

        if actor_id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="DATASET_VALIDATED",
                description=f"Validou dataset com {len(dataset)} registros e {len(errors)} erros.",
            )
        return errors

    def unify_and_store(self, sources: list[list[dict[str, Any]]], actor_id: int | None = None):
        consolidated = self.unify_sources(sources)
        errors = self.validate_dataset(consolidated, actor_id=None)
        run = self.repository.create(
            source_count=len(sources),
            consolidated_data=consolidated,
            validation_errors=errors,
        )
        if actor_id:
            self.activity_service.log(
                user_id=actor_id,
                actor_id=actor_id,
                action="DATASET_UNIFIED",
                description=f"Unificou {len(sources)} fontes em {len(consolidated)} registros.",
            )
        return run

from datetime import datetime, timedelta, timezone

from app.repositories.user_activity_repository import UserActivityRepository


class UserActivityService:
    def __init__(self):
        self.repository = UserActivityRepository()

    def log(self, user_id: int, action: str, description: str, actor_id: int | None = None):
        return self.repository.create(
            user_id=user_id,
            actor_id=actor_id,
            action=action,
            description=description,
        )

    def list_for_user(
        self,
        user_id: int,
        limit: int = 200,
        module: str | None = None,
        action: str | None = None,
        q: str | None = None,
        days: int | None = None,
    ):
        module_actions = self._actions_for_module(module)
        since_dt = None
        if days and days > 0:
            since_dt = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)

        return self.repository.list_by_user(
            user_id=user_id,
            limit=limit,
            action=action,
            actions=module_actions,
            q=q,
            since_dt=since_dt,
        )

    def _actions_for_module(self, module: str | None):
        if not module:
            return None
        key = module.strip().upper()
        mapping = {
            "AUTH": ["LOGIN"],
            "USER": ["USER_CREATED", "USER_UPDATED", "USER_DEACTIVATED"],
            "UNIT": ["UNIT_CREATED", "UNIT_UPDATED"],
            "DEPARTMENT": ["DEPARTMENT_CREATED", "DEPARTMENT_UPDATED"],
            "COURSE": ["COURSE_CREATED", "COURSE_UPDATED"],
            "STUDENT": ["STUDENT_CREATED", "STUDENT_UPDATED", "STUDENT_STATUS_UPDATED", "STUDENT_CONTROL_TABLE_CREATED"],
            "ACADEMIC_YEAR": ["ACADEMIC_YEAR_OPENED"],
            "DATASET": ["DATASET_UNIFIED", "DATASET_VALIDATED"],
            "REPORT": ["REPORT_GENERATED"],
        }
        return mapping.get(key)

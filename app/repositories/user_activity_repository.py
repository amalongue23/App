from app.models.user_activity import UserActivity
from app.repositories.base_repository import BaseRepository


class UserActivityRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserActivity)

    def list_by_user(
        self,
        user_id: int,
        limit: int = 200,
        action: str | None = None,
        actions: list[str] | None = None,
        q: str | None = None,
        since_dt=None,
    ):
        query = UserActivity.query.filter_by(user_id=user_id)
        if action:
            query = query.filter(UserActivity.action == action)
        if actions:
            query = query.filter(UserActivity.action.in_(actions))
        if q:
            pattern = f"%{q}%"
            query = query.filter(UserActivity.description.ilike(pattern))
        if since_dt:
            query = query.filter(UserActivity.created_at >= since_dt)

        return query.order_by(UserActivity.created_at.desc(), UserActivity.id.desc()).limit(limit).all()

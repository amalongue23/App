from functools import wraps

from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_smorest import abort


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")
            if user_role == "ADMIN":
                return fn(*args, **kwargs)
            if user_role not in roles:
                abort(403, message="Access denied for this role")
            return fn(*args, **kwargs)

        return wrapper

    return decorator

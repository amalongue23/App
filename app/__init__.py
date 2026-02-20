from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash

from app.config import Config
from app.controllers.academic_year_controller import blp as academic_year_blp
from app.controllers.auth_controller import blp as auth_blp
from app.controllers.course_controller import blp as course_blp
from app.controllers.dashboard_controller import blp as dashboard_blp
from app.controllers.dataset_controller import blp as dataset_blp
from app.controllers.department_controller import blp as department_blp
from app.controllers.report_controller import blp as report_blp
from app.controllers.student_controller import blp as student_blp
from app.controllers.unit_controller import blp as unit_blp
from app.controllers.user_controller import blp as user_blp
from app.extensions import api, db, jwt
from app.models import academic_year, activity_log, course, course_result, dataset_run, department, department_notice, organizational_unit, professor, student, student_control, user, user_scope  # noqa: F401
from app.models.user import User


def _seed_default_rector_user():
    if User.query.count() > 0:
        return

    default_user = User(
        full_name="System Reitor",
        username="admin",
        password_hash=generate_password_hash("admin123"),
        role="REITOR",
        is_active=True,
    )
    db.session.add(default_user)
    db.session.commit()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=False,
        expose_headers=["Authorization"],
    )

    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

    api.register_blueprint(auth_blp)
    api.register_blueprint(user_blp)
    api.register_blueprint(academic_year_blp)
    api.register_blueprint(unit_blp)
    api.register_blueprint(department_blp)
    api.register_blueprint(course_blp)
    api.register_blueprint(student_blp)
    api.register_blueprint(dataset_blp)
    api.register_blueprint(report_blp)
    api.register_blueprint(dashboard_blp)

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok"})

    with app.app_context():
        db.create_all()
        _seed_default_rector_user()

    return app

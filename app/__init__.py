from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from config import get_config
from app.database.connection import get_db

bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    cfg = get_config()
    app.config.from_object(cfg)
    app.secret_key = cfg.SECRET_KEY

    # Extensions
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # MongoDB
    app.db = get_db(cfg.MONGO_URI, cfg.DB_NAME)

    # Blueprints
    from app.routes.auth import auth_bp
    from app.routes.students import students_bp
    from app.routes.grades import grades_bp
    from app.routes.attendance import attendance_bp
    from app.routes.analytics import analytics_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.courses import courses_bp
    from app.routes.activities import activities_bp
    from app.routes.reports import reports_bp
    from app.routes.admin import admin_bp
    from app.routes.messages import messages_bp
    from app.routes.clubs import clubs_bp
    from app.routes.leaves import leaves_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(grades_bp, url_prefix="/grades")
    app.register_blueprint(attendance_bp, url_prefix="/attendance")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(activities_bp, url_prefix="/activities")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(messages_bp, url_prefix="/messages")
    app.register_blueprint(clubs_bp, url_prefix="/clubs")
    app.register_blueprint(leaves_bp, url_prefix="/leaves")

    # Jinja2 global yardımcılar
    app.jinja_env.globals.update(enumerate=enumerate, zip=zip, len=len, str=str)

    # Jinja2 tarih formatı filtreleri (ISO → DD.MM.YYYY)
    def _fmt_date(val):
        if not val:
            return '—'
        s = str(val)
        try:
            parts = s[:10].split('-')
            if len(parts) == 3:
                return f"{parts[2]}.{parts[1]}.{parts[0]}"
        except Exception:
            pass
        return s[:10]

    def _fmt_datetime(val):
        if not val:
            return '—'
        s = str(val)
        try:
            date_part = s[:10].split('-')
            time_part = s[11:16] if len(s) > 10 else ''
            if len(date_part) == 3:
                d = f"{date_part[2]}.{date_part[1]}.{date_part[0]}"
                return f"{d} {time_part}".strip() if time_part else d
        except Exception:
            pass
        return s[:16]

    app.jinja_env.filters['fmt_date'] = _fmt_date
    app.jinja_env.filters['fmt_datetime'] = _fmt_datetime

    # Context processor — sidebar linkleri için student_id / teacher_id sağlar
    @app.context_processor
    def inject_nav():
        from flask import session
        from bson import ObjectId
        user = session.get("user")
        if not user:
            return {}
        nav = {}
        try:
            uid = ObjectId(user["id"])
            if user["role"] == "student":
                doc = app.db.students.find_one({"user_id": uid}, {"_id": 1})
                if doc:
                    nav["nav_student_id"] = str(doc["_id"])
            elif user["role"] == "teacher":
                doc = app.db.teachers.find_one({"user_id": uid}, {"_id": 1})
                if doc:
                    nav["nav_teacher_id"] = str(doc["_id"])
            nav["nav_unread_messages"] = app.db.messages.count_documents(
                {"receiver_id": uid, "is_read": False}
            )
            if user["role"] == "admin":
                nav["nav_pending_count"] = app.db.users.count_documents({"is_approved": False})
        except Exception:
            pass
        return nav

    # JWT hata yönetimi
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        from flask import jsonify
        return jsonify({"error": "Token süresi dolmuş. Lütfen tekrar giriş yapın."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        from flask import jsonify
        return jsonify({"error": "Geçersiz token."}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        from flask import jsonify
        return jsonify({"error": "Token bulunamadı. Lütfen giriş yapın."}), 401

    return app

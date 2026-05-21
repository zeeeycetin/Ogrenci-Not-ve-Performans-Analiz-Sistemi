from .auth import auth_bp
from .students import students_bp
from .grades import grades_bp
from .attendance import attendance_bp
from .analytics import analytics_bp
from .dashboard import dashboard_bp

__all__ = ["auth_bp", "students_bp", "grades_bp", "attendance_bp", "analytics_bp", "dashboard_bp"]

from functools import wraps
from urllib.parse import urlparse
from flask import request, jsonify, g, redirect, url_for, session
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from datetime import datetime


def _is_browser_request() -> bool:
    """JWT token yoksa ve session da yoksa browser isteği sayılır."""
    return not request.is_json


def _check_session_auth():
    """Session tabanlı kimlik doğrulama (web UI için)."""
    return session.get("user") is not None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Önce session kontrol et (web UI)
        if _check_session_auth():
            return f(*args, **kwargs)
        # JWT kontrol et (API)
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception:
            if _is_browser_request():
                session["_next"] = request.url
                return redirect(url_for("auth.login"))
            return jsonify({"error": "Giriş yapmanız gerekiyor."}), 401
    return decorated


def teacher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Session kontrolü
        if _check_session_auth():
            if session["user"].get("role") != "teacher":
                if _is_browser_request():
                    return redirect(url_for("dashboard.index"))
                return jsonify({"error": "Bu işlem için öğretmen yetkisi gerekiyor."}), 403
            return f(*args, **kwargs)
        # JWT kontrolü
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "teacher":
                return jsonify({"error": "Bu işlem için öğretmen yetkisi gerekiyor."}), 403
        except Exception:
            if _is_browser_request():
                return redirect(url_for("auth.login"))
            return jsonify({"error": "Giriş yapmanız gerekiyor."}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if _check_session_auth():
            if session["user"].get("role") != "admin":
                if _is_browser_request():
                    return redirect(url_for("dashboard.index"))
                return jsonify({"error": "Bu işlem için yönetici yetkisi gerekiyor."}), 403
            return f(*args, **kwargs)
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "admin":
                return jsonify({"error": "Bu işlem için yönetici yetkisi gerekiyor."}), 403
        except Exception:
            if _is_browser_request():
                return redirect(url_for("auth.login"))
            return jsonify({"error": "Giriş yapmanız gerekiyor."}), 401
        return f(*args, **kwargs)
    return decorated


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if _check_session_auth():
            if session["user"].get("role") != "student":
                if _is_browser_request():
                    return redirect(url_for("dashboard.index"))
                return jsonify({"error": "Bu işlem için öğrenci yetkisi gerekiyor."}), 403
            return f(*args, **kwargs)
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "student":
                return jsonify({"error": "Bu işlem için öğrenci yetkisi gerekiyor."}), 403
        except Exception:
            if _is_browser_request():
                return redirect(url_for("auth.login"))
            return jsonify({"error": "Giriş yapmanız gerekiyor."}), 401
        return f(*args, **kwargs)
    return decorated


def get_current_user_id() -> str:
    return get_jwt_identity()


def get_current_role() -> str:
    claims = get_jwt()
    return claims.get("role", "")


def log_login(db, user_id: str, username: str, role: str, ip_address: str, success: bool):
    db.login_logs.insert_one({
        "user_id": user_id,
        "username": username,
        "role": role,
        "ip_address": ip_address,
        "success": success,
        "timestamp": datetime.utcnow(),
    })

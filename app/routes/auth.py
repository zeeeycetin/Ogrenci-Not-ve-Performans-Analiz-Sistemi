from urllib.parse import urlparse
from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, session
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, get_jwt
from app.services.auth_service import AuthService
from app.utils.auth import log_login
from app.utils.helpers import success_response, error_response
from university_data import UNIVERSITY_STRUCTURE

auth_bp = Blueprint("auth", __name__)


def get_auth_service():
    return AuthService(current_app.db)


# -----------------------------------------------------------------
# Kayıt
# -----------------------------------------------------------------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html", university_structure=UNIVERSITY_STRUCTURE)

    data = request.get_json(silent=True) or request.form.to_dict()
    result = get_auth_service().register(data)

    if not result["success"]:
        if request.is_json:
            return error_response("Kayıt başarısız.", 400, result.get("errors"))
        return render_template("auth/register.html", errors=result.get("errors", {}))
    if request.is_json:
        return success_response(
            {"user_id": result["user_id"], "role": result["role"]},
            "Kayıt başarılı.",
            201,
        )
    return redirect(url_for("auth.login"))


# -----------------------------------------------------------------
# Giriş
# -----------------------------------------------------------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user"):
            return redirect(url_for("dashboard.index"))
        return render_template("auth/login.html")

    data = request.get_json(silent=True) or request.form.to_dict()
    identifier = data.get("identifier") or data.get("email") or data.get("username", "")
    password = data.get("password", "")

    result = get_auth_service().login(identifier, password)
    ip = request.remote_addr

    if not result["success"]:
        log_login(current_app.db, "", identifier, "", ip, False)
        if request.is_json:
            return error_response(result["message"], 401)
        msg = result["message"]
        if msg == "pending_approval":
            msg = "Hesabınız henüz yönetici tarafından onaylanmamış. Lütfen bekleyin."
        return render_template("auth/login.html", error=msg)

    user = result["user"]
    log_login(current_app.db, user["id"], user["username"], user["role"], ip, True)

    if not request.is_json:
        session["access_token"] = result["access_token"]
        session["user"] = user
        next_url = session.pop("_next", None)
        if next_url:
            parsed = urlparse(next_url)
            safe_hosts = {request.host, "localhost", "127.0.0.1"}
            if not parsed.netloc or parsed.netloc in safe_hosts:
                return redirect(next_url)
        if user["role"] == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        if user["role"] == "teacher":
            return redirect(url_for("dashboard.teacher_dashboard"))
        return redirect(url_for("dashboard.student_dashboard"))

    return success_response({
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "user": user,
    }, "Giriş başarılı.")


# -----------------------------------------------------------------
# Çıkış
# -----------------------------------------------------------------

@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# -----------------------------------------------------------------
# Şifre değiştir
# -----------------------------------------------------------------

@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    data = request.get_json()
    result = get_auth_service().change_password(
        user_id, data.get("old_password", ""), data.get("new_password", "")
    )
    if not result["success"]:
        return error_response(result["message"], 400)
    return success_response(message=result["message"])


# -----------------------------------------------------------------
# Token yenile
# -----------------------------------------------------------------

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user_doc = current_app.db.users.find_one({"_id": __import__("bson").ObjectId(user_id)})
    if not user_doc:
        return error_response("Kullanıcı bulunamadı.", 404)
    claims = {"role": user_doc["role"], "full_name": user_doc["full_name"]}
    new_token = create_access_token(identity=user_id, additional_claims=claims)
    return success_response({"access_token": new_token})

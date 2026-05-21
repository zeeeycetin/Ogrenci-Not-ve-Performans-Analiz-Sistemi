from flask import Blueprint, request, current_app, render_template, session, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.services.dashboard_service import DashboardService
from app.services.student_service import StudentService
from app.utils.auth import login_required, teacher_required, student_required
from app.utils.helpers import success_response, error_response, serialize_doc

dashboard_bp = Blueprint("dashboard", __name__)


def get_service():
    return DashboardService(current_app.db)


# -----------------------------------------------------------------
# Web UI rotaları (session tabanlı)
# -----------------------------------------------------------------

@dashboard_bp.route("/", methods=["GET"])
def index():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    user = session["user"]
    if user["role"] == "admin":
        return redirect(url_for("admin.admin_dashboard"))
    if user["role"] == "teacher":
        return redirect(url_for("dashboard.teacher_dashboard"))
    return redirect(url_for("dashboard.student_dashboard"))


@dashboard_bp.route("/teacher", methods=["GET"])
def teacher_dashboard():
    if not session.get("user"):
        return redirect(url_for("auth.login"))

    user = session["user"]
    academic_year = request.args.get("academic_year", "2024-2025")

    from bson import ObjectId
    from datetime import datetime
    uid = ObjectId(user["id"])
    teacher_doc = current_app.db.teachers.find_one({"user_id": uid})
    if not teacher_doc:
        # Profil yoksa otomatik oluştur
        now = datetime.utcnow()
        teacher_doc = {
            "user_id": uid,
            "teacher_number": f"T{str(uid)[-5:].upper()}",
            "full_name": user["full_name"],
            "branch": "Belirtilmedi",
            "phone": "",
            "profile_image": "",
            "assigned_classes": [],
            "created_at": now,
            "updated_at": now,
        }
        result = current_app.db.teachers.insert_one(teacher_doc)
        teacher_doc["_id"] = result.inserted_id

    data = get_service().get_teacher_dashboard(str(teacher_doc["_id"]), academic_year)
    stats = get_service().get_system_stats()

    return render_template(
        "dashboard/teacher_dashboard.html",
        dashboard=data,
        stats=stats,
        user=user,
        academic_year=academic_year,
    )


@dashboard_bp.route("/student", methods=["GET"])
def student_dashboard():
    if not session.get("user"):
        return redirect(url_for("auth.login"))

    user = session["user"]
    from bson import ObjectId
    from datetime import datetime
    uid = ObjectId(user["id"])
    student_doc = current_app.db.students.find_one({"user_id": uid})
    if not student_doc:
        # Profil yoksa otomatik oluştur
        now = datetime.utcnow()
        student_doc = {
            "user_id": uid,
            "student_number": f"S{str(uid)[-6:].upper()}",
            "full_name": user["full_name"],
            "class_name": "Belirtilmedi",
            "birth_date": None,
            "gender": "",
            "phone": "",
            "address": "",
            "profile_image": "",
            "created_at": now,
            "updated_at": now,
        }
        result = current_app.db.students.insert_one(student_doc)
        student_doc["_id"] = result.inserted_id

    data = get_service().get_student_dashboard(str(student_doc["_id"]))
    return render_template(
        "dashboard/student_dashboard.html",
        dashboard=data,
        student=student_doc,
        user=user,
    )


# -----------------------------------------------------------------
# API rotaları (JWT tabanlı)
# -----------------------------------------------------------------

@dashboard_bp.route("/api/teacher/<teacher_id>", methods=["GET"])
@teacher_required
def api_teacher_dashboard(teacher_id: str):
    academic_year = request.args.get("academic_year")
    result = get_service().get_teacher_dashboard(teacher_id, academic_year)
    return success_response(result)


@dashboard_bp.route("/api/student/<student_id>", methods=["GET"])
@login_required
def api_student_dashboard(student_id: str):
    result = get_service().get_student_dashboard(student_id)
    return success_response(result)


@dashboard_bp.route("/api/stats", methods=["GET"])
@teacher_required
def api_stats():
    return success_response(get_service().get_system_stats())


# -----------------------------------------------------------------
# Profil sayfası
# -----------------------------------------------------------------

@dashboard_bp.route("/profile", methods=["GET"])
def profile():
    if not session.get("user"):
        return redirect(url_for("auth.login"))

    user = session["user"]
    from bson import ObjectId
    uid = ObjectId(user["id"])

    if user["role"] == "teacher":
        doc = current_app.db.teachers.find_one({"user_id": uid})
        assigned_courses = []
        if doc:
            course_codes = doc.get("assigned_courses", [])
            assigned_courses = serialize_doc(list(
                current_app.db.courses.find({"course_code": {"$in": course_codes}})
            ))
        return render_template("profile/index.html",
            user=user, profile=serialize_doc(doc) if doc else {},
            assigned_courses=assigned_courses)
    else:
        doc = current_app.db.students.find_one({"user_id": uid})
        grades = []
        if doc:
            pipeline = [
                {"$match": {"student_id": doc["_id"]}},
                {"$lookup": {"from": "courses", "localField": "course_id",
                             "foreignField": "_id", "as": "course"}},
                {"$unwind": "$course"},
            ]
            grades = serialize_doc(list(current_app.db.grades.aggregate(pipeline)))
        return render_template("profile/index.html",
            user=user, profile=serialize_doc(doc) if doc else {},
            grades=grades)


# -----------------------------------------------------------------
# Bildirim API
# -----------------------------------------------------------------

@dashboard_bp.route("/api/notifications", methods=["GET"])
@login_required
def api_notifications():
    user = session.get("user", {})
    from bson import ObjectId
    uid = ObjectId(user["id"])

    if user["role"] == "student":
        student = current_app.db.students.find_one({"user_id": uid})
        if student:
            notifs = list(
                current_app.db.notifications.find({"student_id": student["_id"]})
                .sort("created_at", -1).limit(8)
            )
            return success_response(serialize_doc(notifs))
    else:
        # Öğretmen için son 8 bildirimi getir
        notifs = list(
            current_app.db.notifications.find({})
            .sort("created_at", -1).limit(8)
        )
        return success_response(serialize_doc(notifs))

    return success_response([])

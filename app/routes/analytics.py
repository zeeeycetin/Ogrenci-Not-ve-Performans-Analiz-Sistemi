from flask import Blueprint, request, current_app, render_template, session, redirect, url_for
from bson import ObjectId
from bson.errors import InvalidId
from app.analysis.analytics_engine import PerformanceAnalyzer
from app.recommendations.recommendation_engine import RecommendationEngine
from app.utils.auth import login_required, teacher_required
from app.utils.helpers import success_response, error_response, serialize_doc

analytics_bp = Blueprint("analytics", __name__)


def get_analyzer():
    return PerformanceAnalyzer(current_app.db)


def get_recommender():
    return RecommendationEngine(current_app.db)


@analytics_bp.route("/student/<student_id>", methods=["GET"])
@login_required
def student_analysis(student_id: str):
    academic_year = request.args.get("academic_year")

    try:
        oid = ObjectId(student_id)
    except (InvalidId, Exception):
        return redirect(url_for("analytics.analytics_overview"))

    student_doc = current_app.db.students.find_one({"_id": oid})
    if not student_doc:
        return redirect(url_for("analytics.analytics_overview"))
    student = serialize_doc(student_doc)

    result = get_analyzer().analyze_student(student_id, academic_year)
    if "error" in result:
        if request.is_json:
            return error_response(result["error"], 404)
        return render_template("analytics/student_analysis.html", analysis=result, student=student)
    if request.is_json:
        return success_response(result)
    return render_template("analytics/student_analysis.html", analysis=result, student=student)


@analytics_bp.route("/class/<class_name>", methods=["GET"])
@teacher_required
def class_analysis(class_name: str):
    academic_year = request.args.get("academic_year")
    result = get_analyzer().analyze_class(class_name, academic_year)
    if "error" in result:
        return error_response(result["error"], 404)
    if request.is_json:
        return success_response(result)
    return render_template("analytics/class_analysis.html", analysis=result)


@analytics_bp.route("/student/<student_id>/recommendations", methods=["GET"])
@login_required
def get_recommendations(student_id: str):
    recs = get_recommender().get_latest_recommendations(student_id)
    if request.is_json:
        return success_response(recs)
    return render_template("recommendations/list.html", recommendations=recs)


@analytics_bp.route("/student/<student_id>/recommendations/generate", methods=["POST"])
@login_required
def generate_recommendations(student_id: str):
    recs = get_recommender().generate_recommendations(student_id)
    return success_response(recs, f"{len(recs)} öneri üretildi.", 201)


@analytics_bp.route("/overview", methods=["GET"])
@login_required
def analytics_overview():
    user = session.get("user", {})

    if user.get("role") == "teacher":
        uid = ObjectId(user["id"])
        teacher = current_app.db.teachers.find_one({"user_id": uid})
        class_names = []
        if teacher:
            courses = list(current_app.db.courses.find({"teacher_id": teacher["_id"]}))
            class_names = list({c["class_name"] for c in courses})

        students = serialize_doc(list(
            current_app.db.students.find({"class_name": {"$in": class_names}})
            .sort("full_name", 1)
        ))
        return render_template("analytics/teacher_overview.html",
            students=students, class_names=class_names, user=user)

    # Öğrenci → kendi analizine yönlendir
    uid = ObjectId(user["id"])
    student = current_app.db.students.find_one({"user_id": uid})
    if student:
        return redirect(url_for("analytics.student_analysis", student_id=str(student["_id"])))
    return redirect(url_for("dashboard.index"))

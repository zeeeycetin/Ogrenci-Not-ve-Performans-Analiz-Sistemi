from flask import Blueprint, render_template, session, current_app
from bson import ObjectId
from app.utils.auth import login_required
from app.utils.helpers import serialize_doc

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/", methods=["GET"])
@login_required
def list_courses():
    user = session.get("user", {})
    role = user.get("role")

    if role == "teacher":
        uid = ObjectId(user["id"])
        teacher = current_app.db.teachers.find_one({"user_id": uid})
        raw_courses = list(current_app.db.courses.find({"teacher_id": teacher["_id"]})) if teacher else []
    else:
        uid = ObjectId(user["id"])
        student = current_app.db.students.find_one({"user_id": uid})
        raw_courses = list(current_app.db.courses.find({"class_name": student.get("class_name", "")})) if student else []

    enriched = []
    for c in raw_courses:
        stats_list = list(current_app.db.grades.aggregate([
            {"$match": {"course_id": c["_id"]}},
            {"$group": {"_id": None, "avg": {"$avg": "$weighted_average"}, "total": {"$sum": 1}}},
        ]))
        _passing = list(current_app.db.grades.aggregate([
            {"$match": {"course_id": c["_id"], "is_passing": True}},
            {"$group": {"_id": None, "count": {"$sum": 1}}},
        ]))
        s = stats_list[0] if stats_list else {}
        s["passing"] = _passing[0]["count"] if _passing else 0
        c_dict = serialize_doc(c)
        c_dict["grade_count"] = s.get("total", 0)
        c_dict["avg_score"] = round(s.get("avg") or 0, 1)
        c_dict["pass_count"] = s.get("passing", 0)
        c_dict["fail_count"] = c_dict["grade_count"] - c_dict["pass_count"]
        enriched.append(c_dict)

    return render_template("courses/list.html", courses=enriched, role=role, user=user)

from flask import Blueprint, render_template, session, redirect, url_for, current_app
from bson import ObjectId
from app.utils.auth import login_required
from app.utils.helpers import serialize_doc

activities_bp = Blueprint("activities", __name__)


@activities_bp.route("/student", methods=["GET"])
@login_required
def student_activities():
    user = session.get("user", {})
    uid = ObjectId(user["id"])
    student = current_app.db.students.find_one({"user_id": uid})
    if not student:
        return redirect(url_for("dashboard.student_dashboard"))

    activities = serialize_doc(list(current_app.db.activities.find({"student_id": student["_id"]})))

    active_count = sum(1 for a in activities if a.get("is_active"))
    total_hours  = sum(a.get("weekly_hours", 0) for a in activities if a.get("is_active"))
    type_counts  = {}
    for a in activities:
        t = a.get("activity_type", "other")
        type_counts[t] = type_counts.get(t, 0) + 1

    return render_template(
        "activities/student.html",
        activities=activities,
        student=serialize_doc(student),
        active_count=active_count,
        total_hours=round(total_hours, 1),
        type_counts=type_counts,
        user=user,
    )

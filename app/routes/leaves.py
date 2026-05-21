from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from bson import ObjectId
from datetime import datetime
from app.utils.auth import login_required

leaves_bp = Blueprint("leaves", __name__)


def _db():
    return current_app.db


def _fmt(doc):
    doc["_id"] = str(doc["_id"])
    for f in ("requester_id", "teacher_id", "student_id"):
        if f in doc:
            doc[f] = str(doc[f])
    for f in ("start_date", "end_date", "created_at"):
        if isinstance(doc.get(f), datetime):
            doc[f] = doc[f].strftime("%d.%m.%Y")
    return doc


@leaves_bp.route("/", methods=["GET"])
@login_required
def my_leaves():
    db  = _db()
    user = session["user"]
    uid  = ObjectId(user["id"])

    if user["role"] == "teacher":
        profile = db.teachers.find_one({"user_id": uid})
        col     = "teacher_leaves"
        id_key  = "teacher_id"
    else:
        profile = db.students.find_one({"user_id": uid})
        col     = "student_leaves"
        id_key  = "student_id"

    leaves = []
    if profile:
        raw = list(db[col].find({id_key: profile["_id"]}).sort("created_at", -1))
        leaves = [_fmt(l) for l in raw]

    return render_template("leaves/my_leaves.html", leaves=leaves)


@leaves_bp.route("/request", methods=["POST"])
@login_required
def request_leave():
    db   = _db()
    user = session["user"]
    uid  = ObjectId(user["id"])

    if user["role"] == "teacher":
        profile  = db.teachers.find_one({"user_id": uid})
        col      = "teacher_leaves"
        id_key   = "teacher_id"
        name_key = "teacher_name"
    else:
        profile  = db.students.find_one({"user_id": uid})
        col      = "student_leaves"
        id_key   = "student_id"
        name_key = "student_name"

    if not profile:
        flash("Profil bulunamadı.", "danger")
        return redirect(url_for("leaves.my_leaves"))

    start_date = request.form.get("start_date", "")
    end_date   = request.form.get("end_date", "")
    leave_type = request.form.get("leave_type", "")
    reason     = request.form.get("reason", "").strip()

    if not start_date or not end_date or not leave_type or not reason:
        flash("Lütfen tüm alanları doldurun.", "warning")
        return redirect(url_for("leaves.my_leaves"))

    try:
        sd = datetime.strptime(start_date, "%Y-%m-%d")
        ed = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        flash("Geçersiz tarih formatı.", "danger")
        return redirect(url_for("leaves.my_leaves"))

    if ed < sd:
        flash("Bitiş tarihi başlangıç tarihinden önce olamaz.", "warning")
        return redirect(url_for("leaves.my_leaves"))

    db[col].insert_one({
        id_key:     profile["_id"],
        name_key:   profile["full_name"],
        "role":     user["role"],
        "start_date": sd,
        "end_date":   ed,
        "leave_type": leave_type,
        "reason":     reason,
        "status":     "pending",
        "admin_note": "",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })
    flash("İzin / devamsızlık talebiniz yöneticiye iletildi.", "success")
    return redirect(url_for("leaves.my_leaves"))

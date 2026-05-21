from flask import Blueprint, render_template, session, redirect, url_for, request, current_app, flash
from bson import ObjectId
from datetime import datetime
from app.utils.auth import login_required, teacher_required
from app.utils.helpers import serialize_doc
from app.models.club import Club

clubs_bp = Blueprint("clubs", __name__)


@clubs_bp.route("/", methods=["GET"])
@login_required
def list_clubs():
    db = current_app.db
    user = session["user"]
    uid = ObjectId(user["id"])

    clubs = serialize_doc(list(db.clubs.find({"is_active": True}).sort("name", 1)))

    # Öğrenci ise hangi kulüplere üye olduğunu işaretle
    member_ids = []
    if user["role"] == "student":
        student = db.students.find_one({"user_id": uid})
        if student:
            sid = student["_id"]
            for c in clubs:
                raw_members = db.clubs.find_one({"_id": ObjectId(c["id"])}, {"member_ids": 1})
                if raw_members and sid in raw_members.get("member_ids", []):
                    member_ids.append(c["id"])

    return render_template("clubs/list.html", clubs=clubs, member_ids=member_ids, user=user)


@clubs_bp.route("/<club_id>", methods=["GET"])
@login_required
def club_detail(club_id: str):
    db = current_app.db
    user = session["user"]
    uid = ObjectId(user["id"])

    club_doc = db.clubs.find_one({"_id": ObjectId(club_id)})
    if not club_doc:
        flash("Kulüp bulunamadı.", "danger")
        return redirect(url_for("clubs.list_clubs"))

    # Üye listesini çek
    member_docs = serialize_doc(list(db.students.find({"_id": {"$in": club_doc.get("member_ids", [])}})))

    is_member = False
    if user["role"] == "student":
        student = db.students.find_one({"user_id": uid})
        if student and student["_id"] in club_doc.get("member_ids", []):
            is_member = True

    teacher_doc = None
    if club_doc.get("teacher_id"):
        teacher_doc = serialize_doc(db.teachers.find_one({"_id": club_doc["teacher_id"]}))

    return render_template(
        "clubs/detail.html",
        club=serialize_doc(club_doc),
        members=member_docs,
        is_member=is_member,
        teacher=teacher_doc,
        user=user,
    )


@clubs_bp.route("/<club_id>/join", methods=["POST"])
@login_required
def join_club(club_id: str):
    db = current_app.db
    user = session["user"]
    if user["role"] != "student":
        flash("Sadece öğrenciler kulübe katılabilir.", "warning")
        return redirect(url_for("clubs.club_detail", club_id=club_id))

    uid = ObjectId(user["id"])
    student = db.students.find_one({"user_id": uid})
    if not student:
        flash("Öğrenci profili bulunamadı.", "danger")
        return redirect(url_for("clubs.list_clubs"))

    club_doc = db.clubs.find_one({"_id": ObjectId(club_id)})
    if not club_doc:
        flash("Kulüp bulunamadı.", "danger")
        return redirect(url_for("clubs.list_clubs"))

    if len(club_doc.get("member_ids", [])) >= club_doc.get("max_members", 30):
        flash("Kulüp kontenjanı dolu.", "warning")
        return redirect(url_for("clubs.club_detail", club_id=club_id))

    db.clubs.update_one({"_id": ObjectId(club_id)}, {"$addToSet": {"member_ids": student["_id"]}})

    # Aktivite kaydı da ekle
    db.activities.update_one(
        {"student_id": student["_id"], "activity_name": club_doc["name"], "activity_type": "club"},
        {"$set": {
            "student_id": student["_id"],
            "activity_name": club_doc["name"],
            "activity_type": "club",
            "role": "Üye",
            "is_active": True,
            "weekly_hours": 2,
            "created_at": datetime.utcnow(),
        }},
        upsert=True,
    )
    flash(f"'{club_doc['name']}' kulübüne katıldınız.", "success")
    return redirect(url_for("clubs.club_detail", club_id=club_id))


@clubs_bp.route("/<club_id>/leave", methods=["POST"])
@login_required
def leave_club(club_id: str):
    db = current_app.db
    user = session["user"]
    uid = ObjectId(user["id"])
    student = db.students.find_one({"user_id": uid})
    if student:
        db.clubs.update_one({"_id": ObjectId(club_id)}, {"$pull": {"member_ids": student["_id"]}})
        club_doc = db.clubs.find_one({"_id": ObjectId(club_id)})
        if club_doc:
            db.activities.update_one(
                {"student_id": student["_id"], "activity_name": club_doc["name"], "activity_type": "club"},
                {"$set": {"is_active": False}},
            )
    flash("Kulüpten ayrıldınız.", "info")
    return redirect(url_for("clubs.club_detail", club_id=club_id))


@clubs_bp.route("/create", methods=["GET", "POST"])
@teacher_required
def create_club():
    db = current_app.db
    user = session["user"]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Kulüp adı zorunludur.", "warning")
            return redirect(url_for("clubs.create_club"))

        uid = ObjectId(user["id"])
        teacher_doc = db.teachers.find_one({"user_id": uid})

        club = Club(
            name=name,
            description=request.form.get("description", ""),
            teacher_id=teacher_doc["_id"] if teacher_doc else None,
            category=request.form.get("category", "genel"),
            meeting_day=request.form.get("meeting_day", ""),
            meeting_time=request.form.get("meeting_time", ""),
            max_members=int(request.form.get("max_members", 30)),
        )
        db.clubs.insert_one(club.to_dict())
        flash(f"'{name}' kulübü oluşturuldu.", "success")
        return redirect(url_for("clubs.list_clubs"))

    return render_template("clubs/create.html", user=user)


@clubs_bp.route("/<club_id>/delete", methods=["POST"])
@teacher_required
def delete_club(club_id: str):
    db = current_app.db
    db.clubs.update_one({"_id": ObjectId(club_id)}, {"$set": {"is_active": False}})
    flash("Kulüp kapatıldı.", "info")
    return redirect(url_for("clubs.list_clubs"))

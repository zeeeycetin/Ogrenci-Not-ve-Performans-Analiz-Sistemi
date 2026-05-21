from flask import Blueprint, request, current_app, render_template, session, redirect, url_for, flash, send_file, jsonify
from datetime import datetime, date
from bson import ObjectId
from app.services.attendance_service import AttendanceService
from app.utils.auth import teacher_required, login_required
from app.utils.helpers import success_response, error_response, serialize_doc

attendance_bp = Blueprint("attendance", __name__)


def get_service():
    return AttendanceService(current_app.db)


@attendance_bp.route("/overview", methods=["GET"])
@login_required
def overview():
    user = session.get("user", {})
    role = user.get("role")
    svc  = get_service()

    if role == "teacher":
        uid = ObjectId(user["id"])
        teacher = current_app.db.teachers.find_one({"user_id": uid})

        # Öğretmenin tüm atanmış sınıfları
        assigned = []
        if teacher and teacher.get("assigned_classes"):
            assigned = teacher["assigned_classes"]
        # assigned_classes boşsa, öğretmenin derslerinden sınıfları çek
        if not assigned:
            teacher_courses = current_app.db.courses.find(
                {"teacher_id": teacher["_id"]} if teacher else {}
            )
            assigned = sorted({c.get("class_name", "") for c in teacher_courses if c.get("class_name")})

        # Seçili sınıf: query param varsa kullan, yoksa ilk sınıf
        selected_class = request.args.get("class_name", assigned[0] if assigned else "")

        report = svc.get_class_attendance_report(selected_class) if selected_class else []

        for s in report:
            sid = ObjectId(s["_id"]) if not isinstance(s["_id"], ObjectId) else s["_id"]
            s["excused"] = current_app.db.attendance.count_documents(
                {"student_id": sid, "status": "excused"}
            )

        at_risk_count = sum(1 for s in report if s.get("absence_rate", 0) >= 20)
        total_late    = sum(s.get("late", 0) for s in report)
        avg_att       = round(sum(100 - s.get("absence_rate", 0) for s in report) / len(report), 1) if report else 0

        return render_template(
            "attendance/overview.html",
            role="teacher", students=report,
            class_name=selected_class,
            assigned_classes=assigned,
            at_risk_count=at_risk_count,
            total_late=total_late,
            avg_attendance=avg_att,
            user=user,
        )
    else:
        uid     = ObjectId(user["id"])
        student = current_app.db.students.find_one({"user_id": uid})
        if not student:
            return redirect(url_for("dashboard.student_dashboard"))

        sid     = student["_id"]
        summary = svc.get_student_attendance_summary(str(sid))

        courses = list(current_app.db.courses.find({"class_name": student.get("class_name", "")}))
        course_stats = []
        for c in courses:
            q = {"student_id": sid, "course_id": c["_id"]}
            total   = current_app.db.attendance.count_documents(q)
            absent  = current_app.db.attendance.count_documents({**q, "status": "absent"})
            late    = current_app.db.attendance.count_documents({**q, "status": "late"})
            present = current_app.db.attendance.count_documents({**q, "status": "present"})
            absence_rate = round((absent + late * 0.5) / total * 100, 1) if total else 0
            course_stats.append({
                "course_name": c["course_name"],
                "course_code": c["course_code"],
                "total": total, "absent": absent, "late": late, "present": present,
                "absence_rate": absence_rate,
            })

        return render_template(
            "attendance/overview.html",
            role="student", summary=summary,
            course_stats=course_stats,
            student=student, user=user,
        )


@attendance_bp.route("/record", methods=["GET"])
@teacher_required
def record_form():
    user = session.get("user", {})
    uid  = ObjectId(user["id"])

    teacher = current_app.db.teachers.find_one({"user_id": uid})
    if not teacher:
        return redirect(url_for("attendance.overview"))

    courses = list(current_app.db.courses.find({"teacher_id": teacher["_id"]}).sort("course_name", 1))

    course_id       = request.args.get("course_id")
    selected_date   = request.args.get("date", date.today().isoformat())
    selected_period = int(request.args.get("period", 1))

    selected_course = None
    students        = []
    existing_map    = {}
    notes_map       = {}

    if course_id:
        selected_course = current_app.db.courses.find_one({"_id": ObjectId(course_id)})
        if selected_course:
            students = list(
                current_app.db.students.find(
                    {"class_name": selected_course.get("class_name", "")}
                ).sort("full_name", 1)
            )

            date_dt = datetime.fromisoformat(selected_date)
            for s in students:
                rec = current_app.db.attendance.find_one({
                    "student_id": s["_id"],
                    "course_id":  selected_course["_id"],
                    "date":       {"$gte": date_dt.replace(hour=0, minute=0, second=0),
                                   "$lt":  date_dt.replace(hour=23, minute=59, second=59)},
                    "period":     selected_period,
                })
                sid_str = str(s["_id"])
                if rec:
                    existing_map[sid_str] = rec.get("status", "")
                    notes_map[sid_str]    = rec.get("notes", "")

    return render_template(
        "attendance/record.html",
        courses=courses,
        selected_course=selected_course,
        selected_date=selected_date,
        selected_period=selected_period,
        students=students,
        existing_map=existing_map,
        notes_map=notes_map,
        user=user,
    )


@attendance_bp.route("/record", methods=["POST"])
@teacher_required
def record_form_post():
    course_id  = request.form.get("course_id")
    date_str   = request.form.get("date", date.today().isoformat())
    period     = int(request.form.get("period", 1))
    student_ids = request.form.getlist("student_ids")

    if not course_id or not student_ids:
        return redirect(url_for("attendance.record_form"))

    date_dt = datetime.fromisoformat(date_str)
    course_oid = ObjectId(course_id)
    svc = get_service()

    for sid_str in student_ids:
        status = request.form.get(f"status_{sid_str}", "present")
        notes  = request.form.get(f"note_{sid_str}", "")
        student_oid = ObjectId(sid_str)

        current_app.db.attendance.update_one(
            {
                "student_id": student_oid,
                "course_id":  course_oid,
                "date":       {"$gte": date_dt.replace(hour=0, minute=0, second=0),
                               "$lt":  date_dt.replace(hour=23, minute=59, second=59)},
                "period":     period,
            },
            {"$set": {
                "student_id": student_oid,
                "course_id":  course_oid,
                "date":       date_dt,
                "period":     period,
                "status":     status,
                "notes":      notes,
                "updated_at": datetime.utcnow(),
            }},
            upsert=True,
        )

    return redirect(url_for(
        "attendance.record_form",
        course_id=course_id,
        date=date_str,
        period=period,
        saved=1,
    ))


@attendance_bp.route("/", methods=["POST"])
@teacher_required
def record():
    data = request.get_json() or request.form.to_dict()
    result = get_service().record_attendance(data)
    return success_response(message="Yoklama kaydedildi.")


@attendance_bp.route("/student/<student_id>/summary", methods=["GET"])
@login_required
def student_summary(student_id: str):
    course_id = request.args.get("course_id")
    result = get_service().get_student_attendance_summary(student_id, course_id)
    return success_response(result)


@attendance_bp.route("/student/<student_id>/records", methods=["GET"])
@login_required
def student_records(student_id: str):
    course_id = request.args.get("course_id")
    start = request.args.get("start_date")
    end = request.args.get("end_date")
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None
    records = get_service().get_attendance_records(student_id, course_id, start_dt, end_dt)
    if request.is_json:
        return success_response(records)
    return render_template("attendance/records.html", records=records)


@attendance_bp.route("/class/<class_name>/report", methods=["GET"])
@teacher_required
def class_report(class_name: str):
    result = get_service().get_class_attendance_report(class_name)
    return success_response(result)


@attendance_bp.route("/class/<class_name>/at-risk", methods=["GET"])
@teacher_required
def at_risk(class_name: str):
    threshold = float(request.args.get("threshold", 20.0))
    result = get_service().get_at_risk_students(class_name, threshold)
    return success_response(result)


@attendance_bp.route("/qr/<course_id>", methods=["GET"])
@teacher_required
def generate_qr(course_id: str):
    """Ders için QR kod üret; öğrenci bu kodu okutarak yoklamaya katılır."""
    import qrcode
    import io
    import socket

    date_str = request.args.get("date", date.today().isoformat())
    period   = request.args.get("period", "1")

    host = request.host
    # localhost/127.0.0.1 ise gerçek LAN IP'sini bul (telefon erişebilsin)
    if host.startswith("localhost") or host.startswith("127.0.0.1"):
        port = host.split(":")[-1] if ":" in host else ""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            lan_ip = s.getsockname()[0]
            s.close()
            host = f"{lan_ip}:{port}" if port else lan_ip
        except Exception:
            pass

    base_url = f"{request.scheme}://{host}"
    scan_path = url_for("attendance.qr_scan", course_id=course_id, date=date_str, period=period)
    scan_url  = base_url + scan_path

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(scan_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1e293b", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png", max_age=0)


@attendance_bp.route("/qr-scan/<course_id>", methods=["GET", "POST"])
@login_required
def qr_scan(course_id: str):
    """Öğrenci QR kodu okuttuğunda bu sayfaya gelir ve yoklamaya katılır."""
    db = current_app.db
    user = session["user"]

    if user["role"] != "student":
        flash("Bu sayfa sadece öğrenciler içindir.", "warning")
        return redirect(url_for("dashboard.index"))

    date_str = request.args.get("date", date.today().isoformat())
    period   = int(request.args.get("period", 1))

    uid = ObjectId(user["id"])
    student = db.students.find_one({"user_id": uid})
    course  = db.courses.find_one({"_id": ObjectId(course_id)})

    if not student or not course:
        flash("Öğrenci veya ders bulunamadı.", "danger")
        return redirect(url_for("dashboard.student_dashboard"))

    date_dt = datetime.fromisoformat(date_str)
    existing = db.attendance.find_one({
        "student_id": student["_id"],
        "course_id":  course["_id"],
        "date":       {"$gte": date_dt.replace(hour=0, minute=0, second=0),
                       "$lt":  date_dt.replace(hour=23, minute=59, second=59)},
        "period":     period,
    })

    if existing:
        flash("Yoklamaya zaten katıldınız.", "info")
        return render_template("attendance/qr_result.html", course=course, date_str=date_str,
                               already=True, user=user)

    db.attendance.insert_one({
        "student_id": student["_id"],
        "course_id":  course["_id"],
        "date":       date_dt,
        "period":     period,
        "status":     "present",
        "notes":      "QR ile katıldı",
        "updated_at": datetime.utcnow(),
    })
    flash(f"'{course['course_name']}' dersine başarıyla katıldınız.", "success")
    return render_template("attendance/qr_result.html", course=course, date_str=date_str,
                           already=False, user=user)


@attendance_bp.route("/qr-session/<course_id>", methods=["GET"])
@teacher_required
def qr_session(course_id: str):
    """Öğretmen ekranında büyük QR + canlı katılım listesi."""
    db = current_app.db
    date_str = request.args.get("date", date.today().isoformat())
    period   = int(request.args.get("period", 1))
    course   = db.courses.find_one({"_id": ObjectId(course_id)})
    if not course:
        flash("Ders bulunamadı.", "danger")
        return redirect(url_for("attendance.record_form"))
    students = serialize_doc(list(
        db.students.find({"class_name": course.get("class_name", "")}).sort("full_name", 1)
    ))
    return render_template("attendance/qr_session.html",
        course=serialize_doc(course),
        students=students,
        date_str=date_str,
        period=period,
        user=session["user"],
    )


@attendance_bp.route("/qr-session/<course_id>/status", methods=["GET"])
@teacher_required
def qr_session_status(course_id: str):
    """JSON: anlık yoklama durumu (AJAX polling için)."""
    db       = current_app.db
    date_str = request.args.get("date", date.today().isoformat())
    period   = int(request.args.get("period", 1))
    date_dt  = datetime.fromisoformat(date_str)

    records = list(db.attendance.find({
        "course_id": ObjectId(course_id),
        "date": {"$gte": date_dt.replace(hour=0, minute=0, second=0),
                 "$lt":  date_dt.replace(hour=23, minute=59, second=59)},
        "period": period,
    }))

    joined = []
    for r in records:
        s = db.students.find_one({"_id": r["student_id"]}, {"full_name": 1, "student_number": 1})
        if s:
            joined.append({
                "name":   s.get("full_name", "—"),
                "number": s.get("student_number", "—"),
                "status": r.get("status", "present"),
            })

    course  = db.courses.find_one({"_id": ObjectId(course_id)})
    total   = db.students.count_documents({"class_name": course.get("class_name", "")}) if course else 0
    present = sum(1 for r in records if r.get("status") == "present")

    return jsonify({"total": total, "present": present, "joined": joined})

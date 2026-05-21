from flask import Blueprint, render_template, session, redirect, url_for, request, current_app, flash, jsonify
from bson import ObjectId
from datetime import datetime
from app.utils.auth import admin_required
from app.utils.helpers import serialize_doc, success_response, error_response
from university_data import UNIVERSITY_STRUCTURE

admin_bp = Blueprint("admin", __name__)


# ── Yardımcı ─────────────────────────────────────────────────
def _db():
    return current_app.db


# ─────────────────────────────────────────────────────────────
# ANA PANEL
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/", methods=["GET"])
@admin_required
def admin_dashboard():
    db = _db()
    pending_count = db.users.count_documents({"is_approved": False})
    stats = {
        "total_users":    db.users.count_documents({}),
        "total_students": db.students.count_documents({}),
        "total_teachers": db.teachers.count_documents({}),
        "total_courses":  db.courses.count_documents({}),
        "total_grades":   db.grades.count_documents({}),
        "total_clubs":    db.clubs.count_documents({}),
        "total_messages": db.messages.count_documents({}),
        "pending_count":  pending_count,
    }
    recent_users  = serialize_doc(list(db.users.find().sort("created_at", -1).limit(10)))
    pending_users = serialize_doc(list(db.users.find({"is_approved": False}).sort("created_at", -1)))

    # Yüksek devamsızlıklı öğrenciler - ayrı sorgular, Python'da birleştir
    _absent_docs = list(db.attendance.aggregate([
        {"$match": {"status": "absent"}},
        {"$group": {"_id": "$student_id", "count": {"$sum": 1}}},
    ]))
    _late_docs = list(db.attendance.aggregate([
        {"$match": {"status": "late"}},
        {"$group": {"_id": "$student_id", "count": {"$sum": 1}}},
    ]))
    _absent_map = {doc["_id"]: doc["count"] for doc in _absent_docs}
    _late_map   = {doc["_id"]: doc["count"] for doc in _late_docs}
    _all_sids   = set(_absent_map) | set(_late_map)
    _weighted   = sorted(
        [(_sid, _absent_map.get(_sid, 0), _late_map.get(_sid, 0),
          _absent_map.get(_sid, 0) * 1.0 + _late_map.get(_sid, 0) * 0.5)
         for _sid in _all_sids],
        key=lambda x: x[3], reverse=True
    )[:10]
    absent_students = []
    for _sid, _a, _l, _ in _weighted:
        _s = db.students.find_one({"_id": _sid}, {"full_name": 1, "student_number": 1, "class_name": 1})
        absent_students.append({
            "_id":            str(_sid),
            "student_name":   _s.get("full_name", "Silinmiş Öğrenci") if _s else "Silinmiş Öğrenci",
            "student_number": _s.get("student_number", "—") if _s else "—",
            "class_name":     _s.get("class_name", "—") if _s else "—",
            "absent_count":   _a,
            "late_count":     _l,
        })

    # Öğretmen + Öğrenci izin talepleri (bekleyen + son 10'ar)
    def _fmt_leaves(raw, id_key):
        result = []
        for l in raw:
            l["_id"] = str(l["_id"])
            if id_key in l:
                l[id_key] = str(l[id_key])
            for f in ("start_date", "end_date", "created_at"):
                if isinstance(l.get(f), datetime):
                    l[f] = l[f].strftime("%d.%m.%Y")
            result.append(l)
        return result

    teacher_leaves = _fmt_leaves(
        list(db.teacher_leaves.find().sort("created_at", -1).limit(10)), "teacher_id"
    )
    student_leaves = _fmt_leaves(
        list(db.student_leaves.find().sort("created_at", -1).limit(10)), "student_id"
    )
    all_leaves = sorted(
        [dict(l, _col="teacher_leaves") for l in teacher_leaves] +
        [dict(l, _col="student_leaves") for l in student_leaves],
        key=lambda x: x.get("created_at", ""), reverse=True
    )[:15]

    pending_leaves_count = (
        db.teacher_leaves.count_documents({"status": "pending"}) +
        db.student_leaves.count_documents({"status": "pending"})
    )

    return render_template("admin/dashboard.html",
        stats=stats, recent_users=recent_users,
        pending_users=pending_users, user=session["user"],
        absent_students=absent_students,
        all_leaves=all_leaves,
        pending_leaves_count=pending_leaves_count)


# ─────────────────────────────────────────────────────────────
# KULLANICI YÖNETİMİ
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/users", methods=["GET"])
@admin_required
def user_list():
    db = _db()
    role_filter    = request.args.get("role", "")
    status_filter  = request.args.get("status", "")
    query = {}
    if role_filter:
        query["role"] = role_filter
    if status_filter == "pending":
        query["is_approved"] = False
    users = serialize_doc(list(db.users.find(query).sort("created_at", -1)))
    return render_template("admin/users.html",
        users=users, role_filter=role_filter,
        status_filter=status_filter, user=session["user"])


@admin_bp.route("/users/<user_id>/approve", methods=["POST"])
@admin_required
def approve_user(user_id: str):
    db = _db()
    db.users.update_one({"_id": ObjectId(user_id)},
        {"$set": {"is_approved": True, "is_active": True, "updated_at": datetime.utcnow()}})
    flash("Kullanıcı onaylandı.", "success")
    return redirect(request.referrer or url_for("admin.user_list"))


@admin_bp.route("/users/<user_id>/reject", methods=["POST"])
@admin_required
def reject_user(user_id: str):
    db = _db()
    db.users.update_one({"_id": ObjectId(user_id)},
        {"$set": {"is_approved": False, "is_active": False, "updated_at": datetime.utcnow()}})
    flash("Kullanıcı reddedildi.", "warning")
    return redirect(request.referrer or url_for("admin.user_list"))


@admin_bp.route("/users/<user_id>/toggle", methods=["POST"])
@admin_required
def toggle_user(user_id: str):
    db = _db()
    u = db.users.find_one({"_id": ObjectId(user_id)})
    if not u:
        flash("Kullanıcı bulunamadı.", "danger")
        return redirect(url_for("admin.user_list"))
    new_status = not u.get("is_active", True)
    db.users.update_one({"_id": ObjectId(user_id)},
        {"$set": {"is_active": new_status, "updated_at": datetime.utcnow()}})
    flash(f"Kullanıcı {'aktif' if new_status else 'pasif'} edildi.", "success")
    return redirect(url_for("admin.user_list"))


@admin_bp.route("/users/<user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id: str):
    db = _db()
    db.users.delete_one({"_id": ObjectId(user_id)})
    flash("Kullanıcı silindi.", "success")
    return redirect(url_for("admin.user_list"))


@admin_bp.route("/users/create", methods=["GET", "POST"])
@admin_required
def create_user():
    db = _db()
    courses     = serialize_doc(list(db.courses.find().sort([("class_name", 1), ("course_name", 1)])))
    class_names = sorted(filter(None, db.students.distinct("class_name") + db.courses.distinct("class_name")))
    class_names = sorted(set(class_names))
    if request.method == "GET":
        return render_template("admin/create_user.html", user=session["user"],
            courses=courses, class_names=class_names)

    from app.services.auth_service import AuthService
    from flask_bcrypt import generate_password_hash as bcrypt_hash
    data = request.form.to_dict()
    role = data.get("role", "student")

    # ── Yeni şema: öğretmen doğrudan teachers koleksiyonuna ────────────
    if role == "teacher":
        email   = data.get("email", "").strip().lower()
        password = data.get("password", "")
        full_name = data.get("full_name", "").strip()

        if not email or not password or not full_name:
            flash("Ad soyad, e-posta ve şifre zorunludur.", "danger")
            return render_template("admin/create_user.html", user=session["user"],
                courses=courses, class_names=class_names)

        if len(password) < 6:
            flash("Şifre en az 6 karakter olmalıdır.", "danger")
            return render_template("admin/create_user.html", user=session["user"],
                courses=courses, class_names=class_names)

        if db.teachers.find_one({"email": email}) or db.users.find_one({"email": email}):
            flash("Bu e-posta zaten kayıtlı.", "danger")
            return render_template("admin/create_user.html", user=session["user"],
                courses=courses, class_names=class_names)

        course_ids      = [ObjectId(cid) for cid in request.form.getlist("course_ids") if cid]
        direct_classes  = request.form.getlist("direct_class_names")
        student_numbers = request.form.getlist("student_numbers")

        assigned_courses = []
        if course_ids:
            sel = list(db.courses.find({"_id": {"$in": course_ids}}, {"course_code": 1}))
            assigned_courses = [c["course_code"] for c in sel if c.get("course_code")]

        now   = datetime.utcnow()
        count = db.teachers.count_documents({}) + 1
        teacher_id_val = data.get("teacher_number", "").strip() or f"T-{now.year}-{count:03d}"

        new_teacher = {
            "teacher_id":       teacher_id_val,
            "name":             full_name,
            "email":            email,
            "password_hash":    bcrypt_hash(password).decode("utf-8"),
            "department":       data.get("branch", "").strip(),
            "assigned_courses": assigned_courses,
            "assigned_students": student_numbers,
            "assigned_classes": sorted(set(filter(None, direct_classes))),
            "role":             "teacher",
            "created_at":       now,
            "last_login":       None,
        }

        ins = db.teachers.insert_one(new_teacher)
        if course_ids:
            db.courses.update_many({"_id": {"$in": course_ids}},
                {"$set": {"teacher_id": ins.inserted_id}})

        flash("Öğretmen başarıyla oluşturuldu.", "success")
        return redirect(url_for("admin.teacher_list"))

    # ── Öğrenci / Admin: eski akış ─────────────────────────────────────
    data["is_approved"] = True
    result = AuthService(db).register(data, strict_password=False)
    if result["success"]:
        flash("Kullanıcı başarıyla oluşturuldu.", "success")
        return redirect(url_for("admin.user_list"))
    flash("Kullanıcı oluşturulamadı: " + str(result.get("errors", "")), "danger")
    return render_template("admin/create_user.html", user=session["user"],
        courses=courses, class_names=class_names, errors=result.get("errors", {}))


@admin_bp.route("/users/<user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id: str):
    db = _db()
    u = db.users.find_one({"_id": ObjectId(user_id)})
    if not u:
        flash("Kullanıcı bulunamadı.", "danger")
        return redirect(url_for("admin.user_list"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        role      = request.form.get("role", u["role"])
        db.users.update_one({"_id": ObjectId(user_id)},
            {"$set": {"full_name": full_name, "role": role, "updated_at": datetime.utcnow()}})
        if u["role"] == "teacher":
            branch = request.form.get("branch", "").strip()
            teacher = db.teachers.find_one({"user_id": ObjectId(user_id)})
            if teacher:
                new_course_ids = [ObjectId(cid) for cid in request.form.getlist("course_ids") if cid]
                # Eski atamayı bu öğretmenden kaldır
                db.courses.update_many({"teacher_id": teacher["_id"]}, {"$unset": {"teacher_id": ""}})
                assigned_classes = []
                if new_course_ids:
                    selected_courses = list(db.courses.find(
                        {"_id": {"$in": new_course_ids}}, {"class_name": 1}
                    ))
                    assigned_classes = sorted({
                        c.get("class_name", "") for c in selected_courses if c.get("class_name")
                    })
                    db.courses.update_many(
                        {"_id": {"$in": new_course_ids}},
                        {"$set": {"teacher_id": teacher["_id"]}},
                    )
                db.teachers.update_one({"_id": teacher["_id"]}, {"$set": {
                    "full_name": full_name, "branch": branch,
                    "assigned_classes": assigned_classes, "updated_at": datetime.utcnow(),
                }})
        elif u["role"] == "student":
            class_name = request.form.get("class_name", "").strip()
            gender     = request.form.get("gender", "").strip()
            db.students.update_one({"user_id": ObjectId(user_id)},
                {"$set": {"full_name": full_name, "class_name": class_name,
                           "gender": gender, "updated_at": datetime.utcnow()}})
        flash("Kullanıcı güncellendi.", "success")
        return redirect(url_for("admin.user_list"))

    profile = None
    all_courses = []
    teacher_course_ids = set()
    if u["role"] == "teacher":
        profile = serialize_doc(db.teachers.find_one({"user_id": u["_id"]}))
        teacher_doc = db.teachers.find_one({"user_id": u["_id"]})
        if teacher_doc:
            teacher_course_ids = {
                str(c["_id"]) for c in db.courses.find({"teacher_id": teacher_doc["_id"]}, {"_id": 1})
            }
        all_courses = serialize_doc(list(db.courses.find().sort([("class_name", 1), ("course_name", 1)])))
    elif u["role"] == "student":
        profile = serialize_doc(db.students.find_one({"user_id": u["_id"]}))

    class_names = sorted(set(filter(None,
        db.students.distinct("class_name") + db.courses.distinct("class_name")
    )))

    return render_template("admin/edit_user.html",
        u=serialize_doc(u), profile=profile, user=session["user"],
        all_courses=all_courses, teacher_course_ids=teacher_course_ids,
        class_names=class_names)


# ─────────────────────────────────────────────────────────────
# ÖĞRENCİ YÖNETİMİ
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/students", methods=["GET"])
@admin_required
def student_list():
    db = _db()
    class_filter = request.args.get("class_name", "")
    query = {"class_name": class_filter} if class_filter else {}
    students    = serialize_doc(list(db.students.find(query).sort("full_name", 1)))
    classes     = sorted(filter(None, db.students.distinct("class_name")))
    class_names = sorted(set(filter(None,
        db.students.distinct("class_name") + db.courses.distinct("class_name")
    )))
    return render_template("admin/students.html",
        students=students, classes=classes, class_names=class_names,
        class_filter=class_filter, user=session["user"])


@admin_bp.route("/students/<student_id>/delete", methods=["POST"])
@admin_required
def delete_student(student_id: str):
    db = _db()
    db.students.delete_one({"_id": ObjectId(student_id)})
    flash("Öğrenci silindi.", "success")
    return redirect(url_for("admin.student_list"))


@admin_bp.route("/students/<student_id>/edit", methods=["POST"])
@admin_required
def edit_student(student_id: str):
    db = _db()
    data = request.form.to_dict()
    allowed = {"full_name", "class_name", "gender", "phone", "student_number"}
    update = {k: v for k, v in data.items() if k in allowed and v}
    update["updated_at"] = datetime.utcnow()
    db.students.update_one({"_id": ObjectId(student_id)}, {"$set": update})
    flash("Öğrenci güncellendi.", "success")
    return redirect(url_for("admin.student_list"))


# ─────────────────────────────────────────────────────────────
# ÖĞRETMEN YÖNETİMİ
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/teachers", methods=["GET"])
@admin_required
def teacher_list():
    db = _db()
    teachers = serialize_doc(list(db.teachers.find().sort("full_name", 1)))
    courses   = serialize_doc(list(db.courses.find().sort([("class_name", 1), ("course_name", 1)])))

    # teacher_id_str -> set of course_id_str (tek sorguda)
    teacher_course_map: dict = {t["id"]: set() for t in teachers}
    for c in db.courses.find({"teacher_id": {"$exists": True, "$ne": None}}, {"_id": 1, "teacher_id": 1}):
        tid_str = str(c["teacher_id"])
        if tid_str in teacher_course_map:
            teacher_course_map[tid_str].add(str(c["_id"]))

    class_names = sorted(set(filter(None,
        db.students.distinct("class_name") + db.courses.distinct("class_name")
    )))

    # Her öğretmen için görüntüleme alanlarını normalize et (eski + yeni şema uyumu)
    for t in teachers:
        t.setdefault("full_name", t.get("name", ""))
        t.setdefault("branch",    t.get("department", ""))
        t.setdefault("teacher_number", t.get("teacher_id", ""))
        t.setdefault("assigned_classes", [])
        t.setdefault("assigned_courses", [])
        t.setdefault("assigned_students", [])

    students = serialize_doc(list(
        db.students.find({}, {"student_number": 1, "full_name": 1, "class_name": 1})
        .sort([("class_name", 1), ("full_name", 1)])
    ))

    return render_template("admin/teachers.html", teachers=teachers, user=session["user"],
        courses=courses, teacher_course_map=teacher_course_map,
        class_names=class_names, students=students)


@admin_bp.route("/teachers/<teacher_id>/delete", methods=["POST"])
@admin_required
def delete_teacher(teacher_id: str):
    db = _db()
    t = db.teachers.find_one({"_id": ObjectId(teacher_id)})
    if t:
        db.users.delete_one({"_id": t.get("user_id")})
    db.teachers.delete_one({"_id": ObjectId(teacher_id)})
    flash("Öğretmen silindi.", "success")
    return redirect(url_for("admin.teacher_list"))


@admin_bp.route("/teachers/<teacher_id>/edit", methods=["POST"])
@admin_required
def edit_teacher(teacher_id: str):
    db = _db()
    data        = request.form.to_dict()
    teacher_oid = ObjectId(teacher_id)
    teacher     = db.teachers.find_one({"_id": teacher_oid})
    if not teacher:
        flash("Öğretmen bulunamadı.", "danger")
        return redirect(url_for("admin.teacher_list"))

    course_ids         = [ObjectId(cid) for cid in request.form.getlist("course_ids") if cid]
    direct_class_names = request.form.getlist("direct_class_names")
    student_numbers    = request.form.getlist("student_numbers")

    # Eski ders atamalarını kaldır, yenileri ata
    db.courses.update_many({"teacher_id": teacher_oid}, {"$unset": {"teacher_id": ""}})
    assigned_courses = []
    if course_ids:
        sel = list(db.courses.find({"_id": {"$in": course_ids}}, {"course_code": 1}))
        assigned_courses = [c["course_code"] for c in sel if c.get("course_code")]
        db.courses.update_many({"_id": {"$in": course_ids}}, {"$set": {"teacher_id": teacher_oid}})

    assigned_classes = sorted(set(filter(None, direct_class_names)))

    is_new_schema = "password_hash" in teacher

    if is_new_schema:
        update = {
            "name":              data.get("full_name", ""),
            "department":        data.get("branch", ""),
            "assigned_courses":  assigned_courses,
            "assigned_students": student_numbers,
            "assigned_classes":  assigned_classes,
            "updated_at":        datetime.utcnow(),
        }
        if data.get("phone"):
            update["phone"] = data["phone"]
        db.teachers.update_one({"_id": teacher_oid}, {"$set": update})
    else:
        update = {
            "full_name":         data.get("full_name", ""),
            "branch":            data.get("branch", ""),
            "assigned_classes":  assigned_classes,
            "assigned_courses":  assigned_courses,
            "assigned_students": student_numbers,
            "updated_at":        datetime.utcnow(),
        }
        if data.get("phone"):
            update["phone"] = data["phone"]
        db.teachers.update_one({"_id": teacher_oid}, {"$set": update})
        if teacher.get("user_id"):
            db.users.update_one({"_id": teacher["user_id"]},
                {"$set": {"full_name": data.get("full_name", ""), "updated_at": datetime.utcnow()}})

    flash("Öğretmen güncellendi.", "success")
    return redirect(url_for("admin.teacher_list"))


# ─────────────────────────────────────────────────────────────
# İZİN YÖNETİMİ
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/leaves/<col>/<leave_id>/approve", methods=["POST"])
@admin_required
def approve_leave(col: str, leave_id: str):
    db = _db()
    if col not in ("teacher_leaves", "student_leaves"):
        flash("Geçersiz koleksiyon.", "danger")
        return redirect(url_for("admin.admin_dashboard"))
    note = request.form.get("admin_note", "").strip()
    db[col].update_one({"_id": ObjectId(leave_id)},
        {"$set": {"status": "approved", "admin_note": note, "updated_at": datetime.utcnow()}})
    flash("Talep onaylandı.", "success")
    return redirect(request.referrer or url_for("admin.admin_dashboard"))


@admin_bp.route("/leaves/<col>/<leave_id>/reject", methods=["POST"])
@admin_required
def reject_leave(col: str, leave_id: str):
    db = _db()
    if col not in ("teacher_leaves", "student_leaves"):
        flash("Geçersiz koleksiyon.", "danger")
        return redirect(url_for("admin.admin_dashboard"))
    note = request.form.get("admin_note", "").strip()
    db[col].update_one({"_id": ObjectId(leave_id)},
        {"$set": {"status": "rejected", "admin_note": note, "updated_at": datetime.utcnow()}})
    flash("Talep reddedildi.", "warning")
    return redirect(request.referrer or url_for("admin.admin_dashboard"))


# ─────────────────────────────────────────────────────────────
# SİSTEM ANALİZİ (Hafta 4)
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/system-analysis", methods=["GET"])
@admin_required
def system_analysis():
    db = _db()
    import numpy as np

    students = list(db.students.find())
    total_students = len(students)

    # Performans etiket dağılımı
    label_dist = {}
    for s in students:
        lbl = s.get("performance_label", "Belirsiz")
        label_dist[lbl] = label_dist.get(lbl, 0) + 1

    # Ortalama not dağılımı
    avgs = [s.get("overall_average") for s in students if s.get("overall_average") is not None]
    avg_stats = {}
    if avgs:
        arr = np.array(avgs, dtype=float)
        avg_stats = {
            "mean":   round(float(arr.mean()), 2),
            "median": round(float(np.median(arr)), 2),
            "std":    round(float(arr.std()), 2),
            "min":    round(float(arr.min()), 2),
            "max":    round(float(arr.max()), 2),
        }

    # Sınıf bazlı ortalama
    class_avgs = {}
    for s in students:
        cls = s.get("class_name", "Bilinmiyor")
        avg = s.get("overall_average")
        if avg is not None:
            if cls not in class_avgs:
                class_avgs[cls] = []
            class_avgs[cls].append(avg)
    class_summary = [
        {"class_name": cls, "average": round(float(np.mean(vals)), 2), "count": len(vals)}
        for cls, vals in sorted(class_avgs.items())
    ]

    # Risk dağılımı (son analizlerden)
    risk_dist = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for s in students:
        last = db.performance_analysis.find_one(
            {"student_id": s["_id"]}, sort=[("analysis_date", -1)]
        )
        if last:
            r = last.get("data", {}).get("risk_level", "low")
            risk_dist[r] = risk_dist.get(r, 0) + 1

    # Devamsızlık durum dağılımı - ayrı sorgular, Python'da birleştir
    _abs_map = {doc["_id"]: doc["count"] for doc in db.attendance.aggregate([
        {"$match": {"status": "absent"}},
        {"$group": {"_id": "$student_id", "count": {"$sum": 1}}},
    ])}
    _late_map2 = {doc["_id"]: doc["count"] for doc in db.attendance.aggregate([
        {"$match": {"status": "late"}},
        {"$group": {"_id": "$student_id", "count": {"$sum": 1}}},
    ])}
    att_docs = [
        {"_id": _sid,
         "absent": _abs_map.get(_sid, 0),
         "total":  _abs_map.get(_sid, 0) + _late_map2.get(_sid, 0)}
        for _sid in set(_abs_map) | set(_late_map2)
    ]
    total_att = db.attendance.count_documents({})
    att_normal = att_warning = att_critical = 0
    for doc in att_docs:
        total_rec = db.attendance.count_documents({"student_id": doc["_id"]})
        rate = (doc["absent"] + (doc["total"] - doc["absent"]) * 0.5) / total_rec * 100 if total_rec else 0
        if rate >= 30:
            att_critical += 1
        elif rate >= 20:
            att_warning += 1
        else:
            att_normal += 1
    att_normal += total_students - len(att_docs)

    # Trend dağılımı (son analizlerden)
    trend_dist = {"Yükselen": 0, "Düşen": 0, "Stabil": 0, "İlk Analiz": 0, "Belirsiz": 0}
    for s in students:
        last = db.performance_analysis.find_one(
            {"student_id": s["_id"]}, sort=[("analysis_date", -1)]
        )
        if last:
            t = last.get("data", {}).get("grade_trend", {}).get("trend", "Belirsiz")
            trend_dist[t] = trend_dist.get(t, 0) + 1
        else:
            trend_dist["Belirsiz"] += 1

    # Kapsam metrikleri (4.1 doğrulama)
    students_with_grades     = db.grades.distinct("student_id")
    students_with_attendance = db.attendance.distinct("student_id")
    students_with_analysis   = db.performance_analysis.distinct("student_id")

    coverage = {
        "total":            total_students,
        "with_grades":      len(students_with_grades),
        "with_attendance":  len(students_with_attendance),
        "with_analysis":    len(students_with_analysis),
        "grade_pct":        round(len(students_with_grades) / max(total_students, 1) * 100, 1),
        "att_pct":          round(len(students_with_attendance) / max(total_students, 1) * 100, 1),
        "analysis_pct":     round(len(students_with_analysis) / max(total_students, 1) * 100, 1),
    }

    # Risk altındaki öğrenciler tablosu
    at_risk_students = serialize_doc(list(db.students.find({
        "performance_label": {"$in": ["Kritik Seviye", "Sınırda"]}
    }).sort("overall_average", 1).limit(10)))

    return render_template("admin/system_analysis.html",
        user=session["user"],
        label_dist=label_dist,
        avg_stats=avg_stats,
        class_summary=class_summary,
        risk_dist=risk_dist,
        att_dist={"normal": att_normal, "warning": att_warning, "critical": att_critical},
        trend_dist=trend_dist,
        coverage=coverage,
        at_risk_students=at_risk_students,
        total_students=total_students,
    )


# ─────────────────────────────────────────────────────────────
# ÖĞRENCİ PERFORMANSLARI
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/performances", methods=["GET"])
@admin_required
def admin_performances():
    db = _db()
    import re as _re

    class_filter = request.args.get("class_name", "")
    label_filter = request.args.get("performance_label", "")
    search       = request.args.get("search", "").strip()

    query = {}
    if class_filter:
        query["class_name"] = class_filter
    if label_filter:
        query["performance_label"] = label_filter
    if search:
        query["full_name"] = {"$regex": _re.escape(search), "$options": "i"}

    students = serialize_doc(list(db.students.find(query).sort("full_name", 1)))

    # Toplu devamsızlık istatistikleri - ayrı sorgular, Python'da birleştir
    _p_absent = {str(doc["_id"]): doc["count"] for doc in db.attendance.aggregate([
        {"$match": {"status": "absent"}},
        {"$group": {"_id": "$student_id", "count": {"$sum": 1}}},
    ])}
    _p_late = {str(doc["_id"]): doc["count"] for doc in db.attendance.aggregate([
        {"$match": {"status": "late"}},
        {"$group": {"_id": "$student_id", "count": {"$sum": 1}}},
    ])}
    _p_total = {str(doc["_id"]): doc["count"] for doc in db.attendance.aggregate([
        {"$group": {"_id": "$student_id", "count": {"$sum": 1}}},
    ])}
    _p_all_sids = set(_p_absent) | set(_p_late) | set(_p_total)
    att_by_student = {
        _sid: {
            "absent_count": _p_absent.get(_sid, 0),
            "late_count":   _p_late.get(_sid, 0),
            "total_count":  _p_total.get(_sid, 0),
        }
        for _sid in _p_all_sids
    }

    # Son performans analizi (risk seviyesi + tarih)
    analysis_pipeline = [
        {"$sort": {"analysis_date": -1}},
        {"$group": {
            "_id": "$student_id",
            "last_date":  {"$first": "$analysis_date"},
            "risk_level": {"$first": "$data.risk_level"},
            "trend":      {"$first": "$data.grade_trend.trend"},
        }}
    ]
    analysis_by_student = {str(doc["_id"]): doc for doc in db.performance_analysis.aggregate(analysis_pipeline)}

    for s in students:
        sid = s["id"]
        att = att_by_student.get(sid, {})
        s["absent_count"] = att.get("absent_count", 0)
        s["late_count"]   = att.get("late_count", 0)
        s["total_att"]    = att.get("total_count", 0)

        an = analysis_by_student.get(sid, {})
        s["risk_level"]    = an.get("risk_level", "")
        s["grade_trend"]   = an.get("trend", "")
        last_date = an.get("last_date")
        s["last_analysis"] = last_date.strftime("%d.%m.%Y") if hasattr(last_date, "strftime") else ""

        # Analiz yapılmamış öğrencilerde alan yoksa None ata (template |float hatasını önler)
        s.setdefault("overall_average", None)
        s.setdefault("performance_label", "")

    classes = sorted(filter(None, db.students.distinct("class_name")))
    labels  = sorted(filter(None, db.students.distinct("performance_label")))

    # Özet istatistikler
    avgs = [s.get("overall_average") for s in students if s.get("overall_average") is not None]
    passing_count = sum(1 for v in avgs if float(v) >= 50)
    import numpy as _np
    if avgs:
        arr = _np.array(avgs, dtype=float)
        summary = {
            "mean":    round(float(arr.mean()), 1),
            "max":     round(float(arr.max()), 1),
            "min":     round(float(arr.min()), 1),
            "passing": passing_count,
            "total":   len(students),
        }
    else:
        summary = {
            "mean":    0,
            "max":     0,
            "min":     0,
            "passing": passing_count,
            "total":   len(students),
        }

    # Grafik verileri (mevcut filtrelenmiş öğrencilerden hesaplanır)
    label_dist  = {}
    risk_dist   = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    trend_dist  = {"Yükselen": 0, "Stabil": 0, "Düşen": 0, "Diğer": 0}
    score_ranges = {"0–49": 0, "50–59": 0, "60–69": 0, "70–79": 0, "80–89": 0, "90–100": 0}
    class_avgs_raw = {}

    for s in students:
        lbl = s.get("performance_label") or "Belirsiz"
        label_dist[lbl] = label_dist.get(lbl, 0) + 1

        risk = s.get("risk_level") or "low"
        if risk in risk_dist:
            risk_dist[risk] += 1

        trend = s.get("grade_trend") or ""
        if trend in trend_dist:
            trend_dist[trend] += 1
        elif trend:
            trend_dist["Diğer"] += 1

        avg = s.get("overall_average")
        if avg is not None:
            f = float(avg)
            if f < 50:   score_ranges["0–49"]   += 1
            elif f < 60: score_ranges["50–59"]  += 1
            elif f < 70: score_ranges["60–69"]  += 1
            elif f < 80: score_ranges["70–79"]  += 1
            elif f < 90: score_ranges["80–89"]  += 1
            else:        score_ranges["90–100"] += 1

        cls = s.get("class_name") or "Bilinmiyor"
        if avg is not None:
            class_avgs_raw.setdefault(cls, []).append(float(avg))

    class_avg_data = [
        {"class_name": cls, "average": round(sum(vals) / len(vals), 1)}
        for cls, vals in sorted(class_avgs_raw.items())
    ]

    # ── Öğretmen Kalitesi ──────────────────────────────────────
    teachers_raw = list(db.teachers.find().sort("full_name", 1))
    teacher_quality = []
    for t in teachers_raw:
        t_id = str(t["_id"])
        t_classes = t.get("assigned_classes", [])
        t_name    = t.get("full_name", "—")
        t_branch  = t.get("branch", "—")

        if not t_classes:
            teacher_quality.append({
                "id": t_id, "full_name": t_name, "branch": t_branch,
                "classes": [], "total_students": 0,
                "mean_avg": None, "passing": 0, "passing_rate": 0,
                "at_risk": 0, "quality_score": None, "quality_label": "Veri Yok",
            })
            continue

        t_students = list(db.students.find({"class_name": {"$in": t_classes}}))
        total = len(t_students)

        if total == 0:
            teacher_quality.append({
                "id": t_id, "full_name": t_name, "branch": t_branch,
                "classes": t_classes, "total_students": 0,
                "mean_avg": None, "passing": 0, "passing_rate": 0,
                "at_risk": 0, "quality_score": None, "quality_label": "Veri Yok",
            })
            continue

        t_avgs = [float(s["overall_average"]) for s in t_students
                  if s.get("overall_average") is not None]
        t_passing  = sum(1 for v in t_avgs if v >= 50)
        t_at_risk  = sum(1 for s in t_students
                         if s.get("performance_label") in ["Kritik Seviye", "Sınırda"])
        t_mean     = round(sum(t_avgs) / len(t_avgs), 1) if t_avgs else None
        t_pass_rate = round(t_passing / total * 100, 1)

        if t_mean is not None:
            q_score = round(t_mean * 0.6 + t_pass_rate * 0.4, 1)
        else:
            q_score = round(t_pass_rate * 0.4, 1)

        if q_score >= 75:   q_label = "Mükemmel"
        elif q_score >= 60: q_label = "İyi"
        elif q_score >= 45: q_label = "Orta"
        else:               q_label = "Gelişmeli"

        teacher_quality.append({
            "id": t_id, "full_name": t_name, "branch": t_branch,
            "classes": t_classes, "total_students": total,
            "mean_avg": t_mean, "passing": t_passing,
            "passing_rate": t_pass_rate, "at_risk": t_at_risk,
            "quality_score": q_score, "quality_label": q_label,
        })

    teacher_quality.sort(
        key=lambda x: (x["quality_score"] is not None, x["quality_score"] or 0),
        reverse=True
    )
    # ───────────────────────────────────────────────────────────

    return render_template("admin/performances.html",
        students=students, classes=classes, labels=labels,
        class_filter=class_filter, label_filter=label_filter, search=search,
        summary=summary,
        label_dist=label_dist, risk_dist=risk_dist,
        trend_dist=trend_dist, score_ranges=score_ranges,
        class_avg_data=class_avg_data,
        teacher_quality=teacher_quality,
        user=session["user"])


# ─────────────────────────────────────────────────────────────
# LOGLAR
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/logs", methods=["GET"])
@admin_required
def login_logs():
    db = _db()
    logs = serialize_doc(list(db.login_logs.find().sort("timestamp", -1).limit(100)))
    return render_template("admin/logs.html", logs=logs, user=session["user"])

"""
Universite formatinda ornek veri seed scripti.
Calistir: python seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from bson import ObjectId
from flask_bcrypt import generate_password_hash
import random

from dotenv import load_dotenv
load_dotenv()

from app.database.connection import get_db

DB_URI  = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "ogrenci_sistemi")
db = get_db(DB_URI, DB_NAME)


random.seed(42)



DEPARTMENT = "Bilgisayar Muhendisligi"
CLASS_NAME = "1. Sinif - A"
SEMESTER   = "Guz Donemi"
ACAD_YEAR  = "2024-2025"

def pw(plain):
    return generate_password_hash(plain).decode("utf-8")

def now():
    return datetime.utcnow()

def days_ago(n):
    return datetime.utcnow() - timedelta(days=n)

# ──────────────────────────────────────────────
# TEMIZLIK
# ──────────────────────────────────────────────
print("Mevcut seed verileri temizleniyor...")
for col in ["users","students","teachers","courses","grades",
            "attendance","activities","clubs","recommendations",
            "performance_analysis","login_logs",
            "notifications","report_templates"]:
    db[col].delete_many({})
print("Temizlendi.\n")

# ──────────────────────────────────────────────
# OGRETMENLER
# ──────────────────────────────────────────────
teacher_data = [
    {"full_name": "Prof. Dr. Ahmet Yilmaz",  "username": "ogretmen1",
     "email": "ahmet@uni.edu.tr",  "branch": "Bilgisayar Muhendisligi",
     "unvan": "Prof. Dr."},
    {"full_name": "Doc. Dr. Fatma Demir",    "username": "ogretmen2",
     "email": "fatma@uni.edu.tr",  "branch": "Yazilim Muhendisligi",
     "unvan": "Doc. Dr."},
    {"full_name": "Dr. Ogr. Uyesi Mehmet Celik", "username": "ogretmen3",
     "email": "mehmet@uni.edu.tr", "branch": "Elektrik-Elektronik Muh.",
     "unvan": "Dr. Ogr. Uyesi"},
]
teacher_ids = []
teacher_user_ids = []

for idx, t in enumerate(teacher_data):
    uid = ObjectId()
    tid = ObjectId()
    tn  = f"FAC{str(tid)[-5:].upper()}"
    formatted_tid = f"T-{datetime.utcnow().year}-{str(idx+1).zfill(3)}"
    db.users.insert_one({
        "_id": uid, "username": t["username"], "email": t["email"],
        "password_hash": pw("Ogretmen123"), "role": "teacher",
        "full_name": t["full_name"], "is_active": True,
        "created_at": now(), "updated_at": now(),
    })
    db.teachers.insert_one({
        "_id": tid, "user_id": uid,
        "teacher_id": formatted_tid,
        "teacher_number": tn,
        "full_name": t["full_name"], "branch": t["branch"],
        "unvan": t["unvan"], "department": DEPARTMENT,
        "phone": "", "profile_image": "",
        "assigned_classes": [CLASS_NAME],
        "assigned_courses": [],   # ders eklendikten sonra güncellenecek
        "assigned_students": [],  # öğrenci eklendikten sonra güncellenecek
        "last_login": None,
        "created_at": now(), "updated_at": now(),
    })
    teacher_ids.append(tid)
    teacher_user_ids.append(uid)
    print(f"  Ogretmen: {t['full_name']}  ({t['username']} / Ogretmen123)  [{formatted_tid}]")

# ──────────────────────────────────────────────
# DERSLER  (6 ders, 3'u projeli)
# ──────────────────────────────────────────────
# Not agirliklari:
#   Projeli     : Vize %40 + Proje %20 + Final %40
#   Projeli degil: Vize %40 + Final  %60
course_data = [
    {"code": "BLM101", "name": "Programlamaya Giris",  "teacher": 0, "credits": 4, "has_project": True,  "hours": 4},
    {"code": "MAT101", "name": "Matematik I",           "teacher": 0, "credits": 4, "has_project": False, "hours": 4},
    {"code": "FIZ101", "name": "Fizik I",               "teacher": 2, "credits": 3, "has_project": False, "hours": 3},
    {"code": "BLM102", "name": "Veri Yapilari",         "teacher": 0, "credits": 4, "has_project": True,  "hours": 4},
    {"code": "ING101", "name": "Mesleki Ingilizce I",   "teacher": 1, "credits": 2, "has_project": False, "hours": 2},
    {"code": "BLM103", "name": "Veri Tabani Sistemleri","teacher": 1, "credits": 3, "has_project": True,  "hours": 3},
]
course_ids = []
course_meta = []  # has_project bilgisini sakla

for c in course_data:
    cid = ObjectId()
    db.courses.insert_one({
        "_id": cid,
        "course_code": c["code"],
        "course_name": c["name"],
        "teacher_id": teacher_ids[c["teacher"]],
        "credits": c["credits"],
        "class_name": CLASS_NAME,
        "semester": SEMESTER,
        "academic_year": ACAD_YEAR,
        "description": "",
        "weekly_hours": c["hours"],
        "has_project": c["has_project"],
        "department": DEPARTMENT,
        "created_at": now(), "updated_at": now(),
    })
    course_ids.append(cid)
    course_meta.append(c)
    # Öğretmenin assigned_courses listesine ekle
    db.teachers.update_one(
        {"_id": teacher_ids[c["teacher"]]},
        {"$addToSet": {"assigned_courses": c["code"]}}
    )
    proje_label = "(Projeli: Vize40+Proje20+Final40)" if c["has_project"] else "(Vize40+Final60)"
    print(f"  Ders: {c['name']} ({c['code']}) {proje_label}")

# ──────────────────────────────────────────────
# OGRENCILER  (10 ogrenci)
# ──────────────────────────────────────────────
student_profiles = [
    {"full_name": "Zeynep Kaya",   "username": "ogrenci1",  "email": "zeynep@uni.edu.tr",  "perf": "high"},
    {"full_name": "Ali Ozturk",    "username": "ogrenci2",  "email": "ali@uni.edu.tr",      "perf": "medium"},
    {"full_name": "Ayse Sahin",    "username": "ogrenci3",  "email": "ayse@uni.edu.tr",     "perf": "high"},
    {"full_name": "Burak Arslan",  "username": "ogrenci4",  "email": "burak@uni.edu.tr",    "perf": "low"},
    {"full_name": "Elif Yildiz",   "username": "ogrenci5",  "email": "elif@uni.edu.tr",     "perf": "medium"},
    {"full_name": "Can Koc",       "username": "ogrenci6",  "email": "can@uni.edu.tr",      "perf": "medium"},
    {"full_name": "Selin Gunes",   "username": "ogrenci7",  "email": "selin@uni.edu.tr",    "perf": "high"},
    {"full_name": "Emre Dogan",    "username": "ogrenci8",  "email": "emre@uni.edu.tr",     "perf": "low"},
    {"full_name": "Merve Aydin",   "username": "ogrenci9",  "email": "merve@uni.edu.tr",    "perf": "medium"},
    {"full_name": "Kerem Polat",   "username": "ogrenci10", "email": "kerem@uni.edu.tr",    "perf": "low"},
]

score_ranges = {
    "high":   {"vize": (75, 98), "final": (80, 100), "proje": (82, 100)},
    "medium": {"vize": (55, 79), "final": (58, 82),  "proje": (58, 85)},
    "low":    {"vize": (30, 58), "final": (32, 62),  "proje": (35, 62)},
}
absence_rates = {"high": 0.05, "medium": 0.12, "low": 0.25}

student_ids  = []
student_uids = []

for i, sp in enumerate(student_profiles):
    uid = ObjectId()
    sid = ObjectId()
    sno = f"2024BLM{str(i+1).zfill(3)}"

    db.users.insert_one({
        "_id": uid, "username": sp["username"], "email": sp["email"],
        "password_hash": pw("Ogrenci123"), "role": "student",
        "full_name": sp["full_name"], "is_active": True,
        "created_at": now(), "updated_at": now(),
    })
    db.students.insert_one({
        "_id": sid, "user_id": uid, "student_number": sno,
        "full_name": sp["full_name"], "class_name": CLASS_NAME,
        "department": DEPARTMENT,
        "birth_date": datetime(2005, random.randint(1,12), random.randint(1,28)),
        "gender": random.choice(["Erkek", "Kız"]),
        "phone": f"05{random.randint(300000000,399999999)}",
        "address": "Istanbul", "profile_image": "",
        "created_at": now(), "updated_at": now(),
    })
    student_ids.append(sid)
    student_uids.append(uid)
    # Her öğretmenin assigned_students listesine ekle
    for tid in teacher_ids:
        db.teachers.update_one(
            {"_id": tid},
            {"$addToSet": {"assigned_students": sno}}
        )
    print(f"  Ogrenci: {sp['full_name']} ({sp['username']} / Ogrenci123)  [{sp['perf']}]")

# ──────────────────────────────────────────────
# NOTLAR
# Projeli     : Vize*0.40 + Proje*0.20 + Final*0.40
# Projeli degil: Vize*0.40 + Final*0.60
# ──────────────────────────────────────────────
print("\nNotlar ekleniyor...")

def weighted_avg(vize, final, proje=None):
    if proje is not None:
        return round(vize * 0.40 + proje * 0.20 + final * 0.40, 2)
    return round(vize * 0.40 + final * 0.60, 2)

def letter(score):
    for t, l in [(90,"AA"),(85,"BA"),(80,"BB"),(75,"CB"),
                 (70,"CC"),(65,"DC"),(60,"DD"),(50,"FD"),(0,"FF")]:
        if score >= t:
            return l
    return "FF"

for si, (sid, sp) in enumerate(zip(student_ids, student_profiles)):
    rng = score_ranges[sp["perf"]]
    for cid, cmeta in zip(course_ids, course_meta):
        vize  = random.randint(*rng["vize"])
        final = random.randint(*rng["final"])
        proje = random.randint(*rng["proje"]) if cmeta["has_project"] else None
        avg   = weighted_avg(vize, final, proje)
        doc = {
            "_id": ObjectId(),
            "student_id": sid, "course_id": cid,
            "midterm_score": float(vize),
            "final_score":   float(final),
            "project_score": float(proje) if proje is not None else None,
            "weighted_average": avg,
            "letter_grade": letter(avg),
            "is_passing": avg >= 60,
            "notes": "",
            "semester": SEMESTER,
            "academic_year": ACAD_YEAR,
            "created_at": now(), "updated_at": now(),
        }
        db.grades.insert_one(doc)

print(f"  {len(student_ids) * len(course_ids)} not eklendi.")

# ──────────────────────────────────────────────
# DEVAMSIZLIK  (son 60 gun, hafta ici)
# ──────────────────────────────────────────────
print("Devamsizlik kayitlari ekleniyor...")

school_days = []
d = days_ago(60)
while d <= datetime.utcnow():
    if d.weekday() < 5:
        school_days.append(d.replace(hour=9, minute=0, second=0, microsecond=0))
    d += timedelta(days=1)

att_count = 0
for si, (sid, sp) in enumerate(zip(student_ids, student_profiles)):
    rate = absence_rates[sp["perf"]]
    for cid in course_ids:
        for day in school_days:
            r = random.random()
            if r < rate * 0.7:
                status = "absent"
            elif r < rate:
                status = "late"
            elif r < rate + 0.03:
                status = "excused"
            else:
                status = "present"
            db.attendance.insert_one({
                "_id": ObjectId(),
                "student_id": sid, "course_id": cid,
                "date": day, "status": status,
                "absence_weight": 1.0 if status=="absent" else (0.5 if status=="late" else 0),
                "notes": "", "created_at": now(),
            })
            att_count += 1

print(f"  {att_count} devamsizlik kaydi eklendi.")

# ──────────────────────────────────────────────
# AKTIVITELER / KULUPLER
# ──────────────────────────────────────────────
print("Aktiviteler ekleniyor...")
activity_pool = [
    ("Kodlama Kulubu",        "science", 3),
    ("Robotik Takim",         "science", 4),
    ("Satranc Kulubu",        "club",    2),
    ("Basketbol Takimi",      "sport",   4),
    ("Muzik Korosu",          "art",     2),
    ("Girisimcilik Kulubu",   "club",    3),
    ("Yapay Zeka Toplulugu",  "science", 3),
    ("Tiyatro Kulubu",        "club",    3),
]
for si, sid in enumerate(student_ids):
    count = random.randint(0, 3)
    chosen = random.sample(activity_pool, count)
    for act in chosen:
        db.activities.insert_one({
            "_id": ObjectId(),
            "student_id": sid,
            "activity_name": act[0],
            "activity_type": act[1],
            "role": random.choice(["member","captain","secretary"]),
            "start_date": days_ago(90),
            "end_date": None,
            "is_active": True,
            "achievements": [],
            "weekly_hours": float(act[2]),
            "created_at": now(),
        })
print("  Aktiviteler eklendi.")

# ──────────────────────────────────────────────
# ANALIZ + ONERILER
# ──────────────────────────────────────────────
print("Analizler ve oneriler uretiliyor...")

from app.analysis.analytics_engine import PerformanceAnalyzer
from app.recommendations.recommendation_engine import RecommendationEngine

analyzer    = PerformanceAnalyzer(db)
recommender = RecommendationEngine(db)

for sid in student_ids:
    try:
        analyzer.analyze_student(str(sid), ACAD_YEAR)
        recommender.generate_recommendations(str(sid))
    except Exception as e:
        print(f"  Analiz hatasi ({sid}): {e}")

print("  Analizler tamamlandi.")

# ──────────────────────────────────────────────
# RAPOR SABLONLARI
# ──────────────────────────────────────────────
print("Rapor sablonlari olusturuluyor...")
report_templates = [
    {
        "_id": ObjectId(),
        "template_name": "Ogrenci Performans Raporu",
        "template_type": "student",
        "description": "Ogrencinin not, devamsizlik ve aktivite ozeti",
        "sections": [
            {"key": "student_info",        "label": "Ogrenci Bilgileri",       "include": True},
            {"key": "grade_summary",        "label": "Not Ozeti",               "include": True},
            {"key": "attendance_summary",   "label": "Devamsizlik Ozeti",       "include": True},
            {"key": "activity_summary",     "label": "Aktivite Ozeti",          "include": True},
            {"key": "performance_label",    "label": "Performans Etiketi",      "include": True},
            {"key": "recommendations",      "label": "Oneriler",                "include": True},
            {"key": "grade_trend",          "label": "Gelisim Trendi",          "include": True},
        ],
        "created_at": now(),
    },
    {
        "_id": ObjectId(),
        "template_name": "Ogretmen Sinif Raporu",
        "template_type": "teacher",
        "description": "Sinif bazli not ortalamasi, risk ogrencileri ve devamsizlik analizi",
        "sections": [
            {"key": "class_summary",        "label": "Sinif Ozeti",             "include": True},
            {"key": "grade_distribution",   "label": "Not Dagilimi",            "include": True},
            {"key": "at_risk_students",     "label": "Risk Altindaki Ogrenciler","include": True},
            {"key": "attendance_overview",  "label": "Devamsizlik Genel Bakis", "include": True},
            {"key": "top_performers",       "label": "Basarili Ogrenciler",     "include": True},
        ],
        "created_at": now(),
    },
]
db.report_templates.insert_many(report_templates)
print(f"  {len(report_templates)} rapor sablonu olusturuldu.")

# ──────────────────────────────────────────────
# OZET
# ──────────────────────────────────────────────
print("\n" + "="*55)
print("SEED TAMAMLANDI - UNIVERSITE FORMATI")
print("="*55)
print(f"  Ogretmen : {db.teachers.count_documents({})}")
print(f"  Ogrenci  : {db.students.count_documents({})}")
print(f"  Ders     : {db.courses.count_documents({})}")
print(f"  Not      : {db.grades.count_documents({})}")
print(f"  Devamsiz : {db.attendance.count_documents({})}")
print(f"  Aktivite : {db.activities.count_documents({})}")
print(f"  Analiz   : {db.performance_analysis.count_documents({})}")
print(f"  Oneri    : {db.recommendations.count_documents({})}")
print(f"  Bildirim : {db.notifications.count_documents({})}")
print(f"  Rpr Sabl : {db.report_templates.count_documents({})}")
print()
print("Giris bilgileri:")
print("  Ogretmen  -> ogretmen1 / Ogretmen123")
print("  Ogrenci   -> ogrenci1  / Ogrenci123")
print()
print("Not agirliklari:")
print("  Projeli ders    : Vize %40 + Proje %20 + Final %40")
print("  Projeli olmayan : Vize %40 + Final %60")
print("  Projeli dersler : BLM101, BLM102, BLM103")

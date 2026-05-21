from datetime import datetime
from bson import ObjectId
from typing import Optional, List
from app.models.student import Student
from app.utils.helpers import serialize_doc


class StudentService:
    def __init__(self, db):
        self.db = db

    # -----------------------------------------------------------------
    # CRUD
    # -----------------------------------------------------------------

    def create_student(self, data: dict) -> dict:
        if self.db.students.find_one({"student_number": data["student_number"]}):
            return {"success": False, "message": "Bu öğrenci numarası zaten kayıtlı."}

        student = Student(
            user_id=data["user_id"],
            student_number=data["student_number"],
            full_name=data["full_name"],
            class_name=data["class_name"],
            birth_date=data.get("birth_date"),
            gender=data.get("gender", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
        )
        self.db.students.insert_one(student.to_dict())
        return {"success": True, "student_id": str(student._id)}

    def get_student_by_id(self, student_id: str) -> Optional[dict]:
        doc = self.db.students.find_one({"_id": ObjectId(student_id)})
        return serialize_doc(doc) if doc else None

    def get_student_by_user_id(self, user_id: str) -> Optional[dict]:
        doc = self.db.students.find_one({"user_id": ObjectId(user_id)})
        return serialize_doc(doc) if doc else None

    # Cinsiyet normalize haritası
    _GENDER_MAP = {
        "kiz": "Kız", "kız": "Kız", "girl": "Kız", "female": "Kız", "f": "Kız",
        "erkek": "Erkek", "boy": "Erkek", "male": "Erkek", "m": "Erkek",
        "kadin": "Kadın", "kadın": "Kadın",
    }

    @classmethod
    def normalize_gender(cls, val: str) -> str:
        if not val:
            return val
        return cls._GENDER_MAP.get(val.lower().strip(), val)

    def get_all_students(self, class_name: str = None, sort_by: str = "full_name",
                          order: int = 1, page: int = 1, per_page: int = 20) -> dict:
        query = {}
        if class_name:
            query["class_name"] = class_name

        total = self.db.students.count_documents(query)

        # Öğrencileri not ortalamasıyla birlikte getir
        pipeline = [
            {"$match": query},
            {"$lookup": {
                "from": "grades",
                "localField": "_id",
                "foreignField": "student_id",
                "as": "_grades",
            }},
            {"$addFields": {
                "overall_average": {
                    "$cond": [
                        {"$gt": [{"$size": "$_grades"}, 0]},
                        {"$round": [{"$avg": "$_grades.weighted_average"}, 1]},
                        None,
                    ]
                }
            }},
            {"$project": {"_grades": 0}},
            {"$sort": {sort_by: order}},
            {"$skip": (page - 1) * per_page},
            {"$limit": per_page},
        ]
        items = serialize_doc(list(self.db.students.aggregate(pipeline)))

        # Cinsiyet ve performans etiketi normalize et
        for s in items:
            s["gender"] = self.normalize_gender(s.get("gender", ""))
            avg = s.get("overall_average")
            if avg is None:
                s["performance_label"] = "Belirsiz"
            elif avg >= 85:
                s["performance_label"] = "Üstün Başarılı"
            elif avg >= 70:
                s["performance_label"] = "İyi"
            elif avg >= 60:
                s["performance_label"] = "Orta"
            elif avg >= 45:
                s["performance_label"] = "Gelişim Gerekli"
            else:
                s["performance_label"] = "Kritik"

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }

    def update_student(self, student_id: str, data: dict) -> dict:
        allowed = {"full_name", "class_name", "birth_date", "gender", "phone", "address"}
        update_data = {k: v for k, v in data.items() if k in allowed}
        update_data["updated_at"] = datetime.utcnow()

        result = self.db.students.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": update_data},
        )
        if result.matched_count == 0:
            return {"success": False, "message": "Öğrenci bulunamadı."}
        return {"success": True, "message": "Öğrenci güncellendi."}

    def delete_student(self, student_id: str) -> dict:
        result = self.db.students.delete_one({"_id": ObjectId(student_id)})
        if result.deleted_count == 0:
            return {"success": False, "message": "Öğrenci bulunamadı."}
        return {"success": True, "message": "Öğrenci silindi."}

    # -----------------------------------------------------------------
    # Sınıf listesi (özet)
    # -----------------------------------------------------------------

    def get_class_list(self) -> List[str]:
        return self.db.students.distinct("class_name")

    # -----------------------------------------------------------------
    # Öğrenci özet istatistikleri
    # -----------------------------------------------------------------

    def get_student_summary(self, student_id: str) -> dict:
        oid = ObjectId(student_id)

        grade_pipeline = [
            {"$match": {"student_id": oid}},
            {"$group": {"_id": None, "avg": {"$avg": "$weighted_average"}, "total_courses": {"$sum": 1}}},
        ]
        grade_result = list(self.db.grades.aggregate(grade_pipeline))
        _passing_docs = list(self.db.grades.aggregate([
            {"$match": {"student_id": oid, "is_passing": True}},
            {"$group": {"_id": None, "count": {"$sum": 1}}},
        ]))
        grade_stats = grade_result[0] if grade_result else {}
        grade_stats["passing"] = _passing_docs[0]["count"] if _passing_docs else 0

        absence_pipeline = [
            {"$match": {"student_id": oid, "status": "absent"}},
            {"$group": {"_id": None, "total_absent": {"$sum": 1}}},
        ]
        abs_result = list(self.db.attendance.aggregate(absence_pipeline))
        total_absent = abs_result[0]["total_absent"] if abs_result else 0

        activity_count = self.db.activities.count_documents({"student_id": oid, "is_active": True})

        return {
            "average_score": round(grade_stats.get("avg") or 0, 2),
            "total_courses": grade_stats.get("total_courses", 0),
            "passing_courses": grade_stats.get("passing", 0),
            "total_absences": total_absent,
            "active_activities": activity_count,
        }

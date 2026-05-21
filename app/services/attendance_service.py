from datetime import datetime
from bson import ObjectId
from typing import List
from app.models.attendance import Attendance
from app.utils.helpers import serialize_doc


class AttendanceService:
    def __init__(self, db):
        self.db = db

    # -----------------------------------------------------------------
    # Devamsızlık kaydet
    # -----------------------------------------------------------------

    def record_attendance(self, data: dict) -> dict:
        attendance = Attendance(
            student_id=data["student_id"],
            course_id=data["course_id"],
            date=data["date"] if isinstance(data["date"], datetime) else datetime.fromisoformat(data["date"]),
            status=data["status"],
            notes=data.get("notes", ""),
        )
        existing = self.db.attendance.find_one({
            "student_id": attendance.student_id,
            "course_id": attendance.course_id,
            "date": attendance.date,
        })
        if existing:
            self.db.attendance.update_one(
                {"_id": existing["_id"]},
                {"$set": {"status": attendance.status, "notes": attendance.notes}},
            )
            return {"success": True, "action": "updated"}
        else:
            self.db.attendance.insert_one(attendance.to_dict())
            return {"success": True, "action": "created"}

    # -----------------------------------------------------------------
    # Öğrenci devamsızlık özeti
    # -----------------------------------------------------------------

    def get_student_attendance_summary(self, student_id: str, course_id: str = None) -> dict:
        query = {"student_id": ObjectId(student_id)}
        if course_id:
            query["course_id"] = ObjectId(course_id)

        docs = list(self.db.attendance.find(query))
        total = len(docs)
        counts = {"present": 0, "absent": 0, "late": 0, "excused": 0}
        for doc in docs:
            status = doc.get("status", "present")
            counts[status] = counts.get(status, 0) + 1

        absence_rate = round((counts["absent"] + counts["late"] * 0.5) / total * 100, 2) if total > 0 else 0

        return {
            "total_days": total,
            "present": counts["present"],
            "absent": counts["absent"],
            "late": counts["late"],
            "excused": counts["excused"],
            "absence_rate": absence_rate,
            "attendance_rate": round(100 - absence_rate, 2),
        }

    # -----------------------------------------------------------------
    # Devamsızlık kayıtlarını getir
    # -----------------------------------------------------------------

    def get_attendance_records(self, student_id: str, course_id: str = None,
                                start_date: datetime = None, end_date: datetime = None) -> List[dict]:
        query = {"student_id": ObjectId(student_id)}
        if course_id:
            query["course_id"] = ObjectId(course_id)
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = start_date
            if end_date:
                query["date"]["$lte"] = end_date

        docs = list(self.db.attendance.find(query).sort("date", -1))
        return serialize_doc(docs)

    # -----------------------------------------------------------------
    # Sınıf bazlı devamsızlık raporu
    # -----------------------------------------------------------------

    def get_class_attendance_report(self, class_name: str) -> List[dict]:
        students = list(self.db.students.find(
            {"class_name": class_name}, {"full_name": 1, "student_number": 1}
        ))
        if not students:
            return []
        student_ids = [s["_id"] for s in students]

        absent_map = {doc["_id"]: doc["count"] for doc in self.db.attendance.aggregate([
            {"$match": {"student_id": {"$in": student_ids}, "status": "absent"}},
            {"$group": {"_id": "$student_id", "count": {"$sum": 1}}},
        ])}
        late_map = {doc["_id"]: doc["count"] for doc in self.db.attendance.aggregate([
            {"$match": {"student_id": {"$in": student_ids}, "status": "late"}},
            {"$group": {"_id": "$student_id", "count": {"$sum": 1}}},
        ])}
        total_map = {doc["_id"]: doc["count"] for doc in self.db.attendance.aggregate([
            {"$match": {"student_id": {"$in": student_ids}}},
            {"$group": {"_id": "$student_id", "count": {"$sum": 1}}},
        ])}

        result = []
        for s in students:
            sid = s["_id"]
            total = total_map.get(sid, 0)
            absent = absent_map.get(sid, 0)
            late = late_map.get(sid, 0)
            missed_weighted = absent + late * 0.5
            absence_rate = round(missed_weighted / total * 100, 1) if total > 0 else 0
            result.append({
                "_id": sid,
                "full_name": s.get("full_name", ""),
                "student_number": s.get("student_number", ""),
                "total": total,
                "absent": absent,
                "late": late,
                "absence_rate": absence_rate,
            })
        result.sort(key=lambda x: x["absence_rate"], reverse=True)
        return serialize_doc(result)

    # -----------------------------------------------------------------
    # Riskli öğrenciler (devamsızlık > eşik)
    # -----------------------------------------------------------------

    def get_at_risk_students(self, class_name: str, threshold: float = 20.0) -> List[dict]:
        all_students = self.get_class_attendance_report(class_name)
        return [s for s in all_students if s.get("absence_rate", 0) >= threshold]

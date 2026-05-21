from datetime import datetime
from bson import ObjectId
from typing import Optional, List, Dict


# Performans etiketi eşlemeleri (Hafta 3 Raporu)
PERFORMANCE_LABELS = [
    (90, "Üstün Başarılı"),
    (75, "Ortalamanın Üstünde"),
    (60, "Geliştirilmeli"),
    (45, "Sınırda"),
    (0,  "Kritik Seviye"),
]

# Devamsızlık durum eşlemeleri (oran %) - Hafta 3 Raporu
ATTENDANCE_STATUS_LABELS = [
    (30, "Kritik"),
    (20, "Uyarı"),
    (0,  "Normal"),
]


def get_performance_label(average: Optional[float]) -> str:
    if average is None:
        return "Belirsiz"
    for threshold, label in PERFORMANCE_LABELS:
        if average >= threshold:
            return label
    return "Kritik"


def get_attendance_status(absence_rate: float) -> str:
    for threshold, label in ATTENDANCE_STATUS_LABELS:
        if absence_rate >= threshold:
            return label
    return "Normal"


class Student:
    """
    Öğrenci OOP sınıfı — MongoDB 'students' koleksiyonuyla eşleşir.
    user_id alanı, users koleksiyonuyla ilişkiyi kurar.
    """

    def __init__(
        self,
        user_id,
        student_number: str,
        full_name: str,
        class_name: str,
        birth_date: Optional[datetime] = None,
        gender: str = "",
        phone: str = "",
        address: str = "",
        profile_image: str = "",
        performance_label: str = "Belirsiz",
        overall_average: Optional[float] = None,
        attendance_summary: Optional[List[Dict]] = None,
        _id=None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        self._id = _id or ObjectId()
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.student_number = student_number
        self.full_name = full_name
        self.class_name = class_name
        self.birth_date = birth_date
        self.gender = gender
        self.phone = phone
        self.address = address
        self.profile_image = profile_image
        self.performance_label = performance_label
        self.overall_average = overall_average
        # Her ders için: {course_code, course_name, total_weeks, missed_weeks, attendance_pct, status}
        self.attendance_summary = attendance_summary or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    # -----------------------------------------------------------------
    # Derived properties
    # -----------------------------------------------------------------

    @property
    def age(self) -> Optional[int]:
        if self.birth_date:
            today = datetime.utcnow()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    # -----------------------------------------------------------------
    # Serialization
    # -----------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "student_number": self.student_number,
            "full_name": self.full_name,
            "class_name": self.class_name,
            "birth_date": self.birth_date,
            "gender": self.gender,
            "phone": self.phone,
            "address": self.address,
            "profile_image": self.profile_image,
            "performance_label": self.performance_label,
            "overall_average": self.overall_average,
            "attendance_summary": self.attendance_summary,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_public_dict(self) -> dict:
        return {
            "id": str(self._id),
            "user_id": str(self.user_id),
            "student_number": self.student_number,
            "full_name": self.full_name,
            "class_name": self.class_name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "gender": self.gender,
            "phone": self.phone,
            "age": self.age,
            "performance_label": self.performance_label,
            "overall_average": self.overall_average,
            "attendance_summary": self.attendance_summary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        obj = cls.__new__(cls)
        obj._id = data.get("_id", ObjectId())
        obj.user_id = data["user_id"]
        obj.student_number = data["student_number"]
        obj.full_name = data["full_name"]
        obj.class_name = data["class_name"]
        obj.birth_date = data.get("birth_date")
        obj.gender = data.get("gender", "")
        obj.phone = data.get("phone", "")
        obj.address = data.get("address", "")
        obj.profile_image = data.get("profile_image", "")
        obj.performance_label = data.get("performance_label", "Belirsiz")
        obj.overall_average = data.get("overall_average")
        obj.attendance_summary = data.get("attendance_summary", [])
        obj.created_at = data.get("created_at", datetime.utcnow())
        obj.updated_at = data.get("updated_at", datetime.utcnow())
        return obj

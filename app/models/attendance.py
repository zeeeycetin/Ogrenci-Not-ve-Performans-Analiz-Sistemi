from datetime import datetime
from bson import ObjectId


class Attendance:
    """
    Devamsızlık OOP sınıfı — MongoDB 'attendance' koleksiyonuyla eşleşir.
    status: 'present' | 'absent' | 'late' | 'excused'
    """

    STATUS_PRESENT = "present"
    STATUS_ABSENT = "absent"
    STATUS_LATE = "late"
    STATUS_EXCUSED = "excused"

    ABSENCE_WEIGHT = {
        STATUS_PRESENT: 0,
        STATUS_ABSENT: 1.0,
        STATUS_LATE: 0.5,
        STATUS_EXCUSED: 0,
    }

    def __init__(
        self,
        student_id,
        course_id,
        date: datetime,
        status: str,
        notes: str = "",
        _id=None,
        created_at: datetime = None,
    ):
        self._id = _id or ObjectId()
        self.student_id = ObjectId(student_id) if not isinstance(student_id, ObjectId) else student_id
        self.course_id = ObjectId(course_id) if not isinstance(course_id, ObjectId) else course_id
        self.date = date
        self.status = status
        self.notes = notes
        self.created_at = created_at or datetime.utcnow()

    @property
    def absence_weight(self) -> float:
        return self.ABSENCE_WEIGHT.get(self.status, 0)

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "date": self.date,
            "status": self.status,
            "absence_weight": self.absence_weight,
            "notes": self.notes,
            "created_at": self.created_at,
        }

    def to_public_dict(self) -> dict:
        return {
            "id": str(self._id),
            "student_id": str(self.student_id),
            "course_id": str(self.course_id),
            "date": self.date.isoformat() if self.date else None,
            "status": self.status,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Attendance":
        obj = cls.__new__(cls)
        obj._id = data.get("_id", ObjectId())
        obj.student_id = data["student_id"]
        obj.course_id = data["course_id"]
        obj.date = data["date"]
        obj.status = data["status"]
        obj.notes = data.get("notes", "")
        obj.created_at = data.get("created_at", datetime.utcnow())
        return obj

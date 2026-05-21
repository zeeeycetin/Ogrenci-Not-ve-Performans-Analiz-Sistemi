from datetime import datetime
from bson import ObjectId


class Activity:
    """
    Aktivite/Kulüp OOP sınıfı — MongoDB 'activities' koleksiyonuyla eşleşir.
    activity_type: 'club' | 'sport' | 'art' | 'science' | 'other'
    """

    TYPE_CLUB = "club"
    TYPE_SPORT = "sport"
    TYPE_ART = "art"
    TYPE_SCIENCE = "science"
    TYPE_OTHER = "other"

    def __init__(
        self,
        student_id,
        activity_name: str,
        activity_type: str,
        role: str = "member",
        start_date: datetime = None,
        end_date: datetime = None,
        is_active: bool = True,
        achievements: list = None,
        weekly_hours: float = 0,
        _id=None,
        created_at: datetime = None,
    ):
        self._id = _id or ObjectId()
        self.student_id = ObjectId(student_id) if not isinstance(student_id, ObjectId) else student_id
        self.activity_name = activity_name
        self.activity_type = activity_type
        self.role = role
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active
        self.achievements = achievements or []
        self.weekly_hours = weekly_hours
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "student_id": self.student_id,
            "activity_name": self.activity_name,
            "activity_type": self.activity_type,
            "role": self.role,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "is_active": self.is_active,
            "achievements": self.achievements,
            "weekly_hours": self.weekly_hours,
            "created_at": self.created_at,
        }

    def to_public_dict(self) -> dict:
        return {
            "id": str(self._id),
            "student_id": str(self.student_id),
            "activity_name": self.activity_name,
            "activity_type": self.activity_type,
            "role": self.role,
            "is_active": self.is_active,
            "weekly_hours": self.weekly_hours,
            "achievements": self.achievements,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Activity":
        obj = cls.__new__(cls)
        obj._id = data.get("_id", ObjectId())
        obj.student_id = data["student_id"]
        obj.activity_name = data["activity_name"]
        obj.activity_type = data["activity_type"]
        obj.role = data.get("role", "member")
        obj.start_date = data.get("start_date")
        obj.end_date = data.get("end_date")
        obj.is_active = data.get("is_active", True)
        obj.achievements = data.get("achievements", [])
        obj.weekly_hours = data.get("weekly_hours", 0)
        obj.created_at = data.get("created_at", datetime.utcnow())
        return obj

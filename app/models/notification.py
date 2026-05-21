from datetime import datetime
from bson import ObjectId
from typing import Optional


class Notification:
    """
    Bildirim modeli — MongoDB 'notifications' koleksiyonuyla eşleşir.
    Sistem tarafından otomatik üretilen uyarılar (devamsızlık, düşük not, performans değişimi).
    """

    TYPE_ATTENDANCE_WARNING = "attendance_warning"
    TYPE_LOW_GRADE_RISK     = "low_grade_risk"
    TYPE_PERFORMANCE_DROP   = "performance_drop"
    TYPE_PERFORMANCE_RISE   = "performance_rise"
    TYPE_STUDY_PLAN         = "study_plan"
    TYPE_TIME_MANAGEMENT    = "time_management"

    PRIORITY_HIGH   = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW    = "low"

    def __init__(
        self,
        student_id,
        notification_type: str,
        title: str,
        message: str,
        priority: str = PRIORITY_MEDIUM,
        related_course: Optional[str] = None,
        is_read: bool = False,
        _id=None,
        created_at: datetime = None,
    ):
        self._id               = _id or ObjectId()
        self.student_id        = ObjectId(student_id) if not isinstance(student_id, ObjectId) else student_id
        self.notification_type = notification_type
        self.title             = title
        self.message           = message
        self.priority          = priority
        self.related_course    = related_course
        self.is_read           = is_read
        self.created_at        = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "_id":               self._id,
            "student_id":        self.student_id,
            "notification_type": self.notification_type,
            "title":             self.title,
            "message":           self.message,
            "priority":          self.priority,
            "related_course":    self.related_course,
            "is_read":           self.is_read,
            "created_at":        self.created_at,
        }

    def to_public_dict(self) -> dict:
        return {
            "id":                str(self._id),
            "student_id":        str(self.student_id),
            "notification_type": self.notification_type,
            "title":             self.title,
            "message":           self.message,
            "priority":          self.priority,
            "related_course":    self.related_course,
            "is_read":           self.is_read,
            "created_at":        self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        obj = cls.__new__(cls)
        obj._id               = data.get("_id", ObjectId())
        obj.student_id        = data["student_id"]
        obj.notification_type = data["notification_type"]
        obj.title             = data["title"]
        obj.message           = data["message"]
        obj.priority          = data.get("priority", cls.PRIORITY_MEDIUM)
        obj.related_course    = data.get("related_course")
        obj.is_read           = data.get("is_read", False)
        obj.created_at        = data.get("created_at", datetime.utcnow())
        return obj

from datetime import datetime
from bson import ObjectId


class Club:
    def __init__(
        self,
        name: str,
        description: str = "",
        teacher_id=None,
        category: str = "genel",
        meeting_day: str = "",
        meeting_time: str = "",
        max_members: int = 30,
        member_ids: list = None,
        is_active: bool = True,
        _id=None,
        created_at: datetime = None,
    ):
        self._id = _id or ObjectId()
        self.name = name
        self.description = description
        self.teacher_id = ObjectId(teacher_id) if teacher_id and not isinstance(teacher_id, ObjectId) else teacher_id
        self.category = category
        self.meeting_day = meeting_day
        self.meeting_time = meeting_time
        self.max_members = max_members
        self.member_ids = [ObjectId(m) if not isinstance(m, ObjectId) else m for m in (member_ids or [])]
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "name": self.name,
            "description": self.description,
            "teacher_id": self.teacher_id,
            "category": self.category,
            "meeting_day": self.meeting_day,
            "meeting_time": self.meeting_time,
            "max_members": self.max_members,
            "member_ids": self.member_ids,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

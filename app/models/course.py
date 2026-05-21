from datetime import datetime
from bson import ObjectId


class Course:
    """
    Ders OOP sınıfı — MongoDB 'courses' koleksiyonuyla eşleşir.
    """

    def __init__(
        self,
        course_code: str,
        course_name: str,
        teacher_id,
        credits: int,
        class_name: str,
        semester: str,
        academic_year: str,
        description: str = "",
        weekly_hours: int = 2,
        has_project: bool = False,
        department: str = "",
        _id=None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        self._id = _id or ObjectId()
        self.course_code = course_code.upper()
        self.course_name = course_name
        self.teacher_id = ObjectId(teacher_id) if not isinstance(teacher_id, ObjectId) else teacher_id
        self.credits = credits
        self.class_name = class_name
        self.semester = semester
        self.academic_year = academic_year
        self.description = description
        self.weekly_hours = weekly_hours
        self.has_project = has_project
        self.department = department
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "course_code": self.course_code,
            "course_name": self.course_name,
            "teacher_id": self.teacher_id,
            "credits": self.credits,
            "class_name": self.class_name,
            "semester": self.semester,
            "academic_year": self.academic_year,
            "description": self.description,
            "weekly_hours": self.weekly_hours,
            "has_project": self.has_project,
            "department": self.department,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_public_dict(self) -> dict:
        return {
            "id": str(self._id),
            "course_code": self.course_code,
            "course_name": self.course_name,
            "teacher_id": str(self.teacher_id),
            "credits": self.credits,
            "class_name": self.class_name,
            "semester": self.semester,
            "academic_year": self.academic_year,
            "weekly_hours": self.weekly_hours,
            "has_project": self.has_project,
            "department": self.department,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Course":
        obj = cls.__new__(cls)
        obj._id = data.get("_id", ObjectId())
        obj.course_code = data["course_code"]
        obj.course_name = data["course_name"]
        obj.teacher_id = data["teacher_id"]
        obj.credits = data["credits"]
        obj.class_name = data["class_name"]
        obj.semester = data["semester"]
        obj.academic_year = data["academic_year"]
        obj.description = data.get("description", "")
        obj.weekly_hours = data.get("weekly_hours", 2)
        obj.has_project = data.get("has_project", False)
        obj.department = data.get("department", "")
        obj.created_at = data.get("created_at", datetime.utcnow())
        obj.updated_at = data.get("updated_at", datetime.utcnow())
        return obj

from datetime import datetime
from bson import ObjectId
from typing import List, Optional


class Teacher:
    """
    Öğretmen OOP sınıfı — MongoDB 'teachers' koleksiyonuyla eşleşir.
    """

    def __init__(
        self,
        user_id,
        teacher_number: str,
        full_name: str,
        branch: str,
        department: str = "",
        phone: str = "",
        profile_image: str = "",
        assigned_classes: List[str] = None,
        assigned_courses: List[str] = None,
        assigned_students: List[str] = None,
        teacher_id: Optional[str] = None,
        last_login: Optional[datetime] = None,
        _id=None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        self._id = _id or ObjectId()
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.teacher_number = teacher_number
        self.teacher_id = teacher_id or self._generate_teacher_id()
        self.full_name = full_name
        self.branch = branch
        self.department = department
        self.phone = phone
        self.profile_image = profile_image
        self.assigned_classes = assigned_classes or []
        self.assigned_courses = assigned_courses or []    # ders kodları listesi
        self.assigned_students = assigned_students or []  # öğrenci numaraları listesi
        self.last_login = last_login
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def _generate_teacher_id(self) -> str:
        year = datetime.utcnow().year
        suffix = str(self._id)[-3:].upper()
        return f"T-{year}-{suffix}"

    def assign_class(self, class_name: str):
        if class_name not in self.assigned_classes:
            self.assigned_classes.append(class_name)

    def assign_course(self, course_code: str):
        if course_code not in self.assigned_courses:
            self.assigned_courses.append(course_code)

    def assign_student(self, student_number: str):
        if student_number not in self.assigned_students:
            self.assigned_students.append(student_number)

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "teacher_id": self.teacher_id,
            "teacher_number": self.teacher_number,
            "full_name": self.full_name,
            "branch": self.branch,
            "department": self.department,
            "phone": self.phone,
            "profile_image": self.profile_image,
            "assigned_classes": self.assigned_classes,
            "assigned_courses": self.assigned_courses,
            "assigned_students": self.assigned_students,
            "last_login": self.last_login,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_public_dict(self) -> dict:
        return {
            "id": str(self._id),
            "user_id": str(self.user_id),
            "teacher_id": self.teacher_id,
            "teacher_number": self.teacher_number,
            "full_name": self.full_name,
            "branch": self.branch,
            "department": self.department,
            "assigned_classes": self.assigned_classes,
            "assigned_courses": self.assigned_courses,
            "assigned_students": self.assigned_students,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Teacher":
        obj = cls.__new__(cls)
        obj._id = data.get("_id", ObjectId())
        obj.user_id = data["user_id"]
        obj.teacher_number = data["teacher_number"]
        obj.teacher_id = data.get("teacher_id", "")
        obj.full_name = data["full_name"]
        obj.branch = data["branch"]
        obj.department = data.get("department", "")
        obj.phone = data.get("phone", "")
        obj.profile_image = data.get("profile_image", "")
        obj.assigned_classes = data.get("assigned_classes", [])
        obj.assigned_courses = data.get("assigned_courses", [])
        obj.assigned_students = data.get("assigned_students", [])
        obj.last_login = data.get("last_login")
        obj.created_at = data.get("created_at", datetime.utcnow())
        obj.updated_at = data.get("updated_at", datetime.utcnow())
        return obj

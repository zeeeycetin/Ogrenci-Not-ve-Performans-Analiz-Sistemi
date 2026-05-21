from datetime import datetime
from bson import ObjectId
from typing import Optional


LETTER_GRADE_MAP = [
    (90, "AA"), (85, "BA"), (80, "BB"), (75, "CB"),
    (70, "CC"), (65, "DC"), (60, "DD"), (50, "FD"), (0, "FF"),
]

# Ağırlık şemaları
WEIGHTS_NO_PROJECT  = {"midterm": 0.40, "final": 0.60}
WEIGHTS_WITH_PROJECT = {"midterm": 0.40, "project": 0.20, "final": 0.40}


def score_to_letter(score: float) -> str:
    for threshold, letter in LETTER_GRADE_MAP:
        if score >= threshold:
            return letter
    return "FF"


def is_passing(letter: str) -> bool:
    return letter not in ("FF", "FD")


class Grade:
    """
    Not OOP sınıfı — MongoDB 'grades' koleksiyonuyla eşleşir.
    Proje yoksa: vize*0.40 + final*0.60
    Proje varsa : vize*0.40 + proje*0.20 + final*0.40
    """

    def __init__(
        self,
        student_id,
        course_id,
        midterm_score: Optional[float] = None,
        final_score: Optional[float] = None,
        project_score: Optional[float] = None,
        notes: str = "",
        semester: str = "",
        academic_year: str = "",
        _id=None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        self._id = _id or ObjectId()
        self.student_id = ObjectId(student_id) if not isinstance(student_id, ObjectId) else student_id
        self.course_id = ObjectId(course_id) if not isinstance(course_id, ObjectId) else course_id
        self.midterm_score = midterm_score
        self.final_score = final_score
        self.project_score = project_score
        self.notes = notes
        self.semester = semester
        self.academic_year = academic_year
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    # -----------------------------------------------------------------
    # Computed properties
    # -----------------------------------------------------------------

    @property
    def weighted_average(self) -> Optional[float]:
        if self.midterm_score is None or self.final_score is None:
            return None
        if self.project_score is not None:
            w = WEIGHTS_WITH_PROJECT
            avg = (self.midterm_score * w["midterm"]
                   + self.project_score * w["project"]
                   + self.final_score * w["final"])
        else:
            w = WEIGHTS_NO_PROJECT
            avg = self.midterm_score * w["midterm"] + self.final_score * w["final"]
        return round(avg, 2)

    @property
    def letter_grade(self) -> Optional[str]:
        avg = self.weighted_average
        return score_to_letter(avg) if avg is not None else None

    @property
    def is_passing(self) -> Optional[bool]:
        letter = self.letter_grade
        return is_passing(letter) if letter else None

    # -----------------------------------------------------------------
    # Serialization
    # -----------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "midterm_score": self.midterm_score,
            "final_score": self.final_score,
            "project_score": self.project_score,
            "weighted_average": self.weighted_average,
            "letter_grade": self.letter_grade,
            "is_passing": self.is_passing,
            "notes": self.notes,
            "semester": self.semester,
            "academic_year": self.academic_year,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_public_dict(self) -> dict:
        return {
            "id": str(self._id),
            "student_id": str(self.student_id),
            "course_id": str(self.course_id),
            "midterm_score": self.midterm_score,
            "final_score": self.final_score,
            "project_score": self.project_score,
            "weighted_average": self.weighted_average,
            "letter_grade": self.letter_grade,
            "is_passing": self.is_passing,
            "semester": self.semester,
            "academic_year": self.academic_year,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Grade":
        obj = cls.__new__(cls)
        obj._id = data.get("_id", ObjectId())
        obj.student_id = data["student_id"]
        obj.course_id = data["course_id"]
        obj.midterm_score = data.get("midterm_score")
        obj.final_score = data.get("final_score")
        obj.project_score = data.get("project_score")
        obj.notes = data.get("notes", "")
        obj.semester = data.get("semester", "")
        obj.academic_year = data.get("academic_year", "")
        obj.created_at = data.get("created_at", datetime.utcnow())
        obj.updated_at = data.get("updated_at", datetime.utcnow())
        return obj

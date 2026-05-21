from datetime import datetime
from bson import ObjectId
from typing import List, Optional
from app.models.grade import Grade
from app.utils.helpers import serialize_doc
from app.utils.validators import validate_grade_data


class GradeService:
    def __init__(self, db):
        self.db = db

    # -----------------------------------------------------------------
    # Not ekle / güncelle
    # -----------------------------------------------------------------

    def upsert_grade(self, data: dict) -> dict:
        errors = validate_grade_data(data)
        if errors:
            return {"success": False, "errors": errors}

        student_id = ObjectId(data["student_id"])
        course_id = ObjectId(data["course_id"])

        existing = self.db.grades.find_one({
            "student_id": student_id,
            "course_id": course_id,
            "semester": data.get("semester", ""),
            "academic_year": data.get("academic_year", ""),
        })

        grade = Grade(
            student_id=student_id,
            course_id=course_id,
            midterm_score=data.get("midterm_score"),
            final_score=data.get("final_score"),
            project_score=data.get("project_score"),
            notes=data.get("notes", ""),
            semester=data.get("semester", ""),
            academic_year=data.get("academic_year", ""),
        )

        if existing:
            self.db.grades.update_one(
                {"_id": existing["_id"]},
                {"$set": {**grade.to_dict(), "_id": existing["_id"]}},
            )
            return {"success": True, "grade_id": str(existing["_id"]), "action": "updated"}
        else:
            self.db.grades.insert_one(grade.to_dict())
            return {"success": True, "grade_id": str(grade._id), "action": "created"}

    # -----------------------------------------------------------------
    # Sorgular
    # -----------------------------------------------------------------

    def get_student_grades(self, student_id: str, academic_year: str = None) -> List[dict]:
        query = {"student_id": ObjectId(student_id)}
        if academic_year:
            query["academic_year"] = academic_year
        docs = list(self.db.grades.find(query))
        return serialize_doc(docs)

    def get_course_grades(self, course_id: str) -> List[dict]:
        docs = list(self.db.grades.find({"course_id": ObjectId(course_id)}))
        return serialize_doc(docs)

    def get_class_averages(self, class_name: str, academic_year: str = None) -> List[dict]:
        """Belirli sınıf için ders bazlı ortalamalar."""
        match_query = {}
        if academic_year:
            match_query["academic_year"] = academic_year

        _base_stages = [
            {"$match": match_query},
            {"$lookup": {"from": "students", "localField": "student_id", "foreignField": "_id", "as": "student"}},
            {"$unwind": "$student"},
            {"$match": {"student.class_name": class_name}},
            {"$lookup": {"from": "courses", "localField": "course_id", "foreignField": "_id", "as": "course"}},
            {"$unwind": "$course"},
        ]
        main_pipeline = _base_stages + [
            {"$group": {
                "_id": "$course_id",
                "course_name": {"$first": "$course.course_name"},
                "course_code": {"$first": "$course.course_code"},
                "avg_score": {"$avg": "$weighted_average"},
                "student_count": {"$sum": 1},
            }},
            {"$sort": {"course_name": 1}},
        ]
        passing_pipeline = _base_stages + [
            {"$match": {"is_passing": True}},
            {"$group": {"_id": "$course_id", "count": {"$sum": 1}}},
        ]
        rows = serialize_doc(list(self.db.grades.aggregate(main_pipeline)))
        passing_by_cid = {str(doc["_id"]): doc["count"] for doc in self.db.grades.aggregate(passing_pipeline)}
        for row in rows:
            cid = row.get("id") or row.get("_id", "")
            row["passing_count"] = passing_by_cid.get(str(cid), 0)
        return rows

    # -----------------------------------------------------------------
    # Başarısız ders tespiti
    # -----------------------------------------------------------------

    def get_failing_courses(self, student_id: str) -> List[dict]:
        pipeline = [
            {"$match": {"student_id": ObjectId(student_id), "is_passing": False}},
            {"$lookup": {
                "from": "courses",
                "localField": "course_id",
                "foreignField": "_id",
                "as": "course",
            }},
            {"$unwind": "$course"},
            {"$project": {
                "course_name": "$course.course_name",
                "course_code": "$course.course_code",
                "weighted_average": 1,
                "letter_grade": 1,
            }},
        ]
        return serialize_doc(list(self.db.grades.aggregate(pipeline)))

    # -----------------------------------------------------------------
    # Sınıf sıralaması
    # -----------------------------------------------------------------

    def get_class_ranking(self, class_name: str, academic_year: str = None) -> List[dict]:
        query_grade = {}
        if academic_year:
            query_grade["academic_year"] = academic_year

        pipeline = [
            {"$match": query_grade},
            {"$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "_id",
                "as": "student",
            }},
            {"$unwind": "$student"},
            {"$match": {"student.class_name": class_name}},
            {"$group": {
                "_id": "$student_id",
                "full_name": {"$first": "$student.full_name"},
                "student_number": {"$first": "$student.student_number"},
                "avg_score": {"$avg": "$weighted_average"},
                "total_courses": {"$sum": 1},
            }},
            {"$sort": {"avg_score": -1}},
            {"$setWindowFields": {
                "sortBy": {"avg_score": -1},
                "output": {"rank": {"$rank": {}}},
            }},
        ]
        return serialize_doc(list(self.db.grades.aggregate(pipeline)))

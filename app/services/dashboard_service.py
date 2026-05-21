from bson import ObjectId
from app.utils.helpers import serialize_doc


class DashboardService:
    def __init__(self, db):
        self.db = db

    # -----------------------------------------------------------------
    # Öğretmen dashboard verileri
    # -----------------------------------------------------------------

    def get_teacher_dashboard(self, teacher_id: str, academic_year: str = None) -> dict:
        oid = ObjectId(teacher_id)

        teacher_courses = list(self.db.courses.find({"teacher_id": oid}))
        course_ids = [c["_id"] for c in teacher_courses]
        class_names = list({c["class_name"] for c in teacher_courses})

        student_count = self.db.students.count_documents({"class_name": {"$in": class_names}})

        grade_query = {"course_id": {"$in": course_ids}}
        if academic_year:
            grade_query["academic_year"] = academic_year

        grade_pipeline = [
            {"$match": grade_query},
            {"$group": {"_id": None, "overall_avg": {"$avg": "$weighted_average"}, "total_grades": {"$sum": 1}}},
        ]
        grade_stats = list(self.db.grades.aggregate(grade_pipeline))
        _passing_docs = list(self.db.grades.aggregate([
            {"$match": {**grade_query, "is_passing": True}},
            {"$group": {"_id": None, "count": {"$sum": 1}}},
        ]))
        stats = grade_stats[0] if grade_stats else {}
        stats["passing"] = _passing_docs[0]["count"] if _passing_docs else 0

        course_averages_pipeline = [
            {"$match": grade_query},
            {"$lookup": {"from": "courses", "localField": "course_id", "foreignField": "_id", "as": "course"}},
            {"$unwind": "$course"},
            {"$group": {
                "_id": "$course_id",
                "course_name": {"$first": "$course.course_name"},
                "avg_score": {"$avg": "$weighted_average"},
                "count": {"$sum": 1},
            }},
            {"$sort": {"avg_score": -1}},
        ]

        top_bottom_pipeline = [
            {"$match": grade_query},
            {"$group": {
                "_id": "$student_id",
                "avg_score": {"$avg": "$weighted_average"},
            }},
            {"$lookup": {"from": "students", "localField": "_id", "foreignField": "_id", "as": "student"}},
            {"$unwind": "$student"},
            {"$project": {
                "full_name": "$student.full_name",
                "student_number": "$student.student_number",
                "class_name": "$student.class_name",
                "avg_score": 1,
            }},
        ]
        all_students = list(self.db.grades.aggregate(top_bottom_pipeline))
        all_students.sort(key=lambda x: x.get("avg_score") or 0, reverse=True)

        return {
            "student_count": student_count,
            "course_count": len(teacher_courses),
            "overall_average": round(stats.get("overall_avg") or 0, 2),
            "pass_rate": round(stats.get("passing", 0) / max(stats.get("total_grades", 1), 1) * 100, 2),
            "course_averages": serialize_doc(list(self.db.grades.aggregate(course_averages_pipeline))),
            "top_students": serialize_doc(all_students[:5]),
            "bottom_students": serialize_doc(all_students[-5:]),
            "class_names": class_names,
        }

    # -----------------------------------------------------------------
    # Öğrenci dashboard verileri
    # -----------------------------------------------------------------

    def get_student_dashboard(self, student_id: str) -> dict:
        oid = ObjectId(student_id)

        grades = list(self.db.grades.find({"student_id": oid}))
        avg = sum(g.get("weighted_average") or 0 for g in grades) / len(grades) if grades else 0

        failing_courses = [g for g in grades if not g.get("is_passing", True)]

        attendance_pipeline = [
            {"$match": {"student_id": oid}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
            }},
        ]
        att_stats = {doc["_id"]: doc["count"] for doc in self.db.attendance.aggregate(attendance_pipeline)}
        total_att = sum(att_stats.values())
        absent_count = att_stats.get("absent", 0)
        absence_rate = round(absent_count / total_att * 100, 2) if total_att else 0

        activities = list(self.db.activities.find({"student_id": oid, "is_active": True}))

        recommendations = list(
            self.db.recommendations.find({"student_id": oid})
            .sort("created_at", -1)
            .limit(5)
        )

        grade_trend_pipeline = [
            {"$match": {"student_id": oid}},
            {"$lookup": {"from": "courses", "localField": "course_id", "foreignField": "_id", "as": "course"}},
            {"$unwind": "$course"},
            {"$project": {
                "course_name": "$course.course_name",
                "has_project": "$course.has_project",
                "weighted_average": 1,
                "letter_grade": 1,
                "is_passing": 1,
                "midterm_score": 1,
                "final_score": 1,
                "project_score": 1,
                "semester": 1,
            }},
            {"$sort": {"course.course_name": 1}},
        ]

        return {
            "overall_average": round(avg, 2),
            "total_courses": len(grades),
            "failing_courses_count": len(failing_courses),
            "absence_rate": absence_rate,
            "total_absences": absent_count,
            "active_activities": len(activities),
            "grade_details": serialize_doc(list(self.db.grades.aggregate(grade_trend_pipeline))),
            "recent_recommendations": serialize_doc(recommendations),
            "activities": serialize_doc(activities),
        }

    # -----------------------------------------------------------------
    # Genel sistem istatistikleri (admin/başlangıç ekranı)
    # -----------------------------------------------------------------

    def get_system_stats(self) -> dict:
        return {
            "total_students": self.db.students.count_documents({}),
            "total_teachers": self.db.teachers.count_documents({}),
            "total_courses": self.db.courses.count_documents({}),
            "total_grades": self.db.grades.count_documents({}),
        }

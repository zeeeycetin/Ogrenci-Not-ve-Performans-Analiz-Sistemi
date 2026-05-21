import numpy as np
import pandas as pd
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
from app.utils.helpers import serialize_doc
from app.models.student import get_performance_label, get_attendance_status


class PerformanceAnalyzer:
    """
    Öğrenci performans analizi motoru.
    Ağırlıklı ortalama, harf notu, devamsızlık korelasyonu,
    aktivite etkisi ve sınıf kıyaslaması hesaplar.
    """

    RISK_THRESHOLDS = {
        "low_grade": 60.0,        # Bu puanın altı başarısız riski
        "high_absence": 20.0,     # % devamsızlık kritik eşiği
        "low_activity": 0,        # Hiç aktivite yoksa uyarı
    }

    def __init__(self, db):
        self.db = db

    # -----------------------------------------------------------------
    # Ana analiz metodu
    # -----------------------------------------------------------------

    def analyze_student(self, student_id: str, academic_year: str = None) -> dict:
        oid = ObjectId(student_id)
        grades = self._get_grades(oid, academic_year)
        attendance = self._get_attendance(oid)
        activities = self._get_activities(oid)

        if not grades:
            return {"error": "Henüz not verisi bulunmamaktadır."}

        grade_analysis = self._analyze_grades(grades)
        attendance_analysis = self._analyze_attendance(attendance)
        activity_analysis = self._analyze_activities(activities)
        correlation = self._calculate_attendance_grade_correlation(grades, attendance)
        risk_level = self._calculate_risk_level(grade_analysis, attendance_analysis, activity_analysis)

        overall_avg = grade_analysis.get("overall_average")
        trend = self._calculate_grade_trend(oid, overall_avg)
        attendance_per_course = self._summarize_attendance_per_course(oid)

        # Çok boyutlu performans skoru: %70 not, %20 devamsızlık (ters), %10 aktivite bonusu + trend
        composite_score = self._calculate_composite_score(
            overall_avg,
            attendance_analysis.get("absence_rate", 0),
            activity_analysis.get("active_activities", 0),
            trend_change=trend.get("change"),
        )
        performance_label = get_performance_label(composite_score)
        confidence = self._calculate_confidence(
            len(grades),
            attendance_analysis.get("total_records", 0),
            activity_analysis.get("total_activities", 0),
        )

        analysis = {
            "student_id": student_id,
            "analysis_date": datetime.utcnow().isoformat(),
            "academic_year": academic_year,
            "composite_score": composite_score,
            "performance_label": performance_label,
            "confidence_score": confidence,
            "grade_analysis": grade_analysis,
            "attendance_analysis": attendance_analysis,
            "attendance_per_course": attendance_per_course,
            "activity_analysis": activity_analysis,
            "attendance_grade_correlation": correlation,
            "risk_level": risk_level,
            "grade_trend": trend,
            "weak_subjects": self._identify_weak_subjects(grades),
            "strong_subjects": self._identify_strong_subjects(grades),
        }

        self._save_analysis(oid, analysis)
        self._update_student_summary(oid, overall_avg, performance_label, attendance_per_course)
        return analysis

    # -----------------------------------------------------------------
    # Not analizi
    # -----------------------------------------------------------------

    def _get_grades(self, student_id: ObjectId, academic_year: str = None) -> List[dict]:
        query = {"student_id": student_id}
        if academic_year:
            query["academic_year"] = academic_year
        pipeline = [
            {"$match": query},
            {"$lookup": {
                "from": "courses",
                "localField": "course_id",
                "foreignField": "_id",
                "as": "course",
            }},
            {"$unwind": "$course"},
        ]
        return list(self.db.grades.aggregate(pipeline))

    def _analyze_grades(self, grades: List[dict]) -> dict:
        scores = [g.get("weighted_average") for g in grades if g.get("weighted_average") is not None]

        if not scores:
            return {}

        arr = np.array(scores, dtype=float)
        return {
            "overall_average": round(float(np.mean(arr)), 2),
            "median": round(float(np.median(arr)), 2),
            "std_deviation": round(float(np.std(arr)), 2),
            "min_score": round(float(np.min(arr)), 2),
            "max_score": round(float(np.max(arr)), 2),
            "total_courses": len(scores),
            "passing_courses": int(np.sum(arr >= 60)),
            "failing_courses": int(np.sum(arr < 60)),
            "pass_rate": round(float(np.mean(arr >= 60)) * 100, 2),
            "course_breakdown": [
                {
                    "course_name": g["course"]["course_name"],
                    "course_code": g["course"]["course_code"],
                    "score": g.get("weighted_average"),
                    "letter_grade": g.get("letter_grade"),
                    "is_passing": g.get("is_passing"),
                }
                for g in grades
            ],
        }

    # -----------------------------------------------------------------
    # Devamsızlık analizi
    # -----------------------------------------------------------------

    def _get_attendance(self, student_id: ObjectId) -> List[dict]:
        return list(self.db.attendance.find({"student_id": student_id}))

    def _analyze_attendance(self, records: List[dict]) -> dict:
        if not records:
            return {"total": 0, "absence_rate": 0, "status": "veri yok"}

        df = pd.DataFrame(records)
        total = len(df)
        counts = df["status"].value_counts().to_dict()

        absent = counts.get("absent", 0)
        late = counts.get("late", 0)
        weighted_absence = absent + late * 0.5
        absence_rate = round(weighted_absence / total * 100, 2)

        return {
            "total_records": total,
            "present": counts.get("present", 0),
            "absent": absent,
            "late": late,
            "excused": counts.get("excused", 0),
            "absence_rate": absence_rate,
            "attendance_rate": round(100 - absence_rate, 2),
            "risk": absence_rate >= self.RISK_THRESHOLDS["high_absence"],
        }

    # -----------------------------------------------------------------
    # Aktivite analizi
    # -----------------------------------------------------------------

    def _get_activities(self, student_id: ObjectId) -> List[dict]:
        return list(self.db.activities.find({"student_id": student_id}))

    def _analyze_activities(self, activities: List[dict]) -> dict:
        total = len(activities)
        active = sum(1 for a in activities if a.get("is_active"))
        weekly_hours = sum(a.get("weekly_hours", 0) for a in activities if a.get("is_active"))
        types = list({a.get("activity_type", "other") for a in activities})

        return {
            "total_activities": total,
            "active_activities": active,
            "weekly_activity_hours": round(weekly_hours, 1),
            "activity_types": types,
            "has_social_activity": any(
                a.get("activity_type") in ("club", "sport", "art") for a in activities
            ),
        }

    # -----------------------------------------------------------------
    # Devamsızlık - not korelasyonu
    # -----------------------------------------------------------------

    def _calculate_attendance_grade_correlation(
        self, grades: List[dict], attendance: List[dict]
    ) -> dict:
        if not grades or not attendance:
            return {"correlation": None, "interpretation": "Yeterli veri yok."}

        course_absence = {}
        for rec in attendance:
            cid = str(rec.get("course_id", ""))
            if rec.get("status") == "absent":
                course_absence[cid] = course_absence.get(cid, 0) + 1

        pairs = []
        for g in grades:
            cid = str(g.get("course_id", ""))
            score = g.get("weighted_average")
            absence = course_absence.get(cid, 0)
            if score is not None:
                pairs.append((absence, score))

        if len(pairs) < 2:
            return {"correlation": None, "interpretation": "Yeterli veri yok."}

        absences = np.array([p[0] for p in pairs], dtype=float)
        scores = np.array([p[1] for p in pairs], dtype=float)

        if np.std(absences) == 0 or np.std(scores) == 0:
            return {"correlation": 0.0, "interpretation": "Değişkenlik yok."}

        corr = float(np.corrcoef(absences, scores)[0, 1])
        if corr < -0.5:
            interpretation = "Güçlü negatif ilişki: Devamsızlık arttıkça not düşüyor."
        elif corr < 0:
            interpretation = "Zayıf negatif ilişki: Devamsızlığın notu hafifçe etkilediği görünüyor."
        else:
            interpretation = "Pozitif veya nötr ilişki."

        return {"correlation": round(corr, 3), "interpretation": interpretation}

    # Çok boyutlu performans skoru: %70 not, %20 devamsızlık (ters), %10 aktivite bonusu
    def _calculate_composite_score(self, grade_avg, absence_rate, active_activities,
                                   trend_change=None) -> float:
        grade_score      = float(grade_avg) if grade_avg is not None else 0.0
        attendance_score = max(0.0, 100.0 - float(absence_rate))
        activity_score   = min(int(active_activities), 5) * 20.0

        # Trend bonusu: belirgin yükseliş/düşüş etkisi
        trend_bonus = 0.0
        if trend_change is not None:
            if trend_change > 5:
                trend_bonus = 3.0
            elif trend_change < -5:
                trend_bonus = -2.0

        raw = 0.70 * grade_score + 0.20 * attendance_score + 0.10 * activity_score + trend_bonus
        return round(max(0.0, min(100.0, raw)), 2)

    def _calculate_confidence(self, grade_count: int, attendance_count: int,
                               activity_count: int) -> float:
        """0–1 arası güven skoru; daha fazla veri daha güvenilir sonuç demektir."""
        grade_conf = min(grade_count / 5.0, 1.0)
        att_conf   = min(attendance_count / 20.0, 1.0)
        act_conf   = 1.0 if activity_count > 0 else 0.5
        return round(grade_conf * 0.5 + att_conf * 0.4 + act_conf * 0.1, 2)

    # -----------------------------------------------------------------
    # Zayıf / güçlü ders tespiti
    # -----------------------------------------------------------------

    def _identify_weak_subjects(self, grades: List[dict]) -> List[dict]:
        return [
            {
                "course_name": g["course"]["course_name"],
                "score": g.get("weighted_average"),
                "letter_grade": g.get("letter_grade"),
            }
            for g in grades
            if (g.get("weighted_average") or 100) < 70
        ]

    def _identify_strong_subjects(self, grades: List[dict]) -> List[dict]:
        return [
            {
                "course_name": g["course"]["course_name"],
                "score": g.get("weighted_average"),
                "letter_grade": g.get("letter_grade"),
            }
            for g in grades
            if (g.get("weighted_average") or 0) >= 85
        ]

    # -----------------------------------------------------------------
    # Risk seviyesi
    # -----------------------------------------------------------------

    def _calculate_risk_level(self, grade_analysis: dict, attendance_analysis: dict,
                               activity_analysis: dict) -> str:
        risk_score = 0
        avg = grade_analysis.get("overall_average", 100)
        absence_rate = attendance_analysis.get("absence_rate", 0)

        if avg < 50:
            risk_score += 3
        elif avg < 60:
            risk_score += 2
        elif avg < 70:
            risk_score += 1

        if absence_rate >= 30:
            risk_score += 3
        elif absence_rate >= 20:
            risk_score += 2
        elif absence_rate >= 10:
            risk_score += 1

        if not activity_analysis.get("has_social_activity"):
            risk_score += 1

        if risk_score >= 5:
            return "critical"
        elif risk_score >= 3:
            return "high"
        elif risk_score >= 1:
            return "medium"
        return "low"

    # -----------------------------------------------------------------
    # Gelişim trendi hesaplama
    # -----------------------------------------------------------------

    def _calculate_grade_trend(self, student_id: ObjectId, current_avg: Optional[float]) -> dict:
        """Son 3 analizi karşılaştırarak 'Yükselen', 'Düşen' veya 'Stabil' trendi döndürür."""
        if current_avg is None:
            return {"trend": "Belirsiz", "change": None, "history": []}

        past = list(
            self.db.performance_analysis.find({"student_id": student_id})
            .sort("analysis_date", -1)
            .limit(3)
        )
        history = [
            round(p.get("data", {}).get("grade_analysis", {}).get("overall_average", 0), 2)
            for p in past
            if p.get("data", {}).get("grade_analysis", {}).get("overall_average") is not None
        ]

        if not history:
            return {"trend": "İlk Analiz", "change": None, "history": []}

        change = round(current_avg - history[0], 2)
        if change > 5:
            trend = "Yükselen"
        elif change < -5:
            trend = "Düşen"
        else:
            trend = "Stabil"

        return {"trend": trend, "change": change, "history": history}

    # -----------------------------------------------------------------
    # Ders bazlı devamsızlık özeti
    # -----------------------------------------------------------------

    def _summarize_attendance_per_course(self, student_id: ObjectId) -> List[dict]:
        """Her ders için toplam hafta, devamsız hafta, % katılım ve durum etiketini döndürür."""
        from collections import defaultdict
        records = list(self.db.attendance.find({"student_id": student_id}))
        course_stats: dict = defaultdict(lambda: {"total": 0, "absent": 0, "late": 0, "excused": 0, "present": 0})
        for rec in records:
            cid = rec["course_id"]
            course_stats[cid]["total"] += 1
            status = rec.get("status", "present")
            if status in course_stats[cid]:
                course_stats[cid][status] += 1
            else:
                course_stats[cid]["present"] += 1

        result = []
        for cid, st in course_stats.items():
            course = self.db.courses.find_one({"_id": cid})
            total = st["total"]
            absent = st["absent"]
            late = st["late"]
            missed_weighted = absent + late * 0.5
            absence_pct = round(missed_weighted / total * 100, 1) if total > 0 else 0
            attendance_pct = round(100 - absence_pct, 1)
            result.append({
                "course_code":    course.get("course_code", "") if course else "",
                "course_name":    course.get("course_name", "") if course else "",
                "total_weeks":    total,
                "missed_weeks":   absent,
                "late_weeks":     late,
                "attendance_pct": attendance_pct,
                "absence_pct":    absence_pct,
                "status":         get_attendance_status(absence_pct),
            })
        return result

    # -----------------------------------------------------------------
    # Öğrenci kaydını güncelle (performans etiketi + devamsızlık özeti)
    # -----------------------------------------------------------------

    def _update_student_summary(
        self,
        student_id: ObjectId,
        overall_avg: Optional[float],
        performance_label: str,
        attendance_summary: List[dict],
    ):
        self.db.students.update_one(
            {"_id": student_id},
            {"$set": {
                "performance_label": performance_label,
                "overall_average": overall_avg,
                "attendance_summary": attendance_summary,
                "updated_at": datetime.utcnow(),
            }},
        )

    # -----------------------------------------------------------------
    # Analizi veritabanına kaydet
    # -----------------------------------------------------------------

    def _save_analysis(self, student_id: ObjectId, analysis: dict):
        self.db.performance_analysis.insert_one({
            "student_id": student_id,
            "analysis_date": datetime.utcnow(),
            "data": {k: v for k, v in analysis.items() if k != "student_id"},
        })

    # -----------------------------------------------------------------
    # Sınıf bazlı analiz
    # -----------------------------------------------------------------

    def analyze_class(self, class_name: str, academic_year: str = None) -> dict:
        students = list(self.db.students.find({"class_name": class_name}))
        if not students:
            return {"error": "Sınıfta öğrenci bulunamadı."}

        all_avgs = []
        risk_students = []

        for s in students:
            sid = s["_id"]
            query = {"student_id": sid}
            if academic_year:
                query["academic_year"] = academic_year

            grades = list(self.db.grades.find(query))
            scores = [g.get("weighted_average") for g in grades if g.get("weighted_average") is not None]
            if scores:
                avg = float(np.mean(scores))
                all_avgs.append(avg)
                if avg < self.RISK_THRESHOLDS["low_grade"]:
                    risk_students.append({
                        "student_id": str(sid),
                        "full_name": s["full_name"],
                        "student_number": s["student_number"],
                        "average": round(avg, 2),
                    })

        if not all_avgs:
            return {"error": "Not verisi bulunamadı."}

        arr = np.array(all_avgs)
        return {
            "class_name": class_name,
            "student_count": len(students),
            "class_average": round(float(np.mean(arr)), 2),
            "class_median": round(float(np.median(arr)), 2),
            "std_deviation": round(float(np.std(arr)), 2),
            "highest_average": round(float(np.max(arr)), 2),
            "lowest_average": round(float(np.min(arr)), 2),
            "at_risk_students": risk_students,
        }

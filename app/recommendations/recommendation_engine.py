from bson import ObjectId
from datetime import datetime
from typing import List, Dict


class RecommendationEngine:
    """
    Rule-based öneri sistemi.
    Öğrencinin not, devamsızlık ve aktivite verilerini analiz ederek
    kişiselleştirilmiş öneriler ve bildirimler üretir.
    """

    PRIORITY_HIGH   = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW    = "low"

    CATEGORY_GRADE          = "grade"
    CATEGORY_ATTENDANCE     = "attendance"
    CATEGORY_ACTIVITY       = "activity"
    CATEGORY_PERFORMANCE    = "performance"
    CATEGORY_STUDY_PLAN     = "study_plan"
    CATEGORY_TIME_MGMT      = "time_management"

    def __init__(self, db):
        self.db = db

    # -----------------------------------------------------------------
    # Ana öneri üretme metodu
    # -----------------------------------------------------------------

    def generate_recommendations(self, student_id: str) -> List[Dict]:
        oid = ObjectId(student_id)
        recommendations = []

        recommendations.extend(self._grade_based_recommendations(oid))
        recommendations.extend(self._attendance_based_recommendations(oid))
        recommendations.extend(self._activity_based_recommendations(oid))
        recommendations.extend(self._performance_trend_recommendations(oid))
        recommendations.extend(self._study_plan_recommendations(oid))
        recommendations.extend(self._time_management_recommendations(oid))

        if recommendations:
            self._save_recommendations(oid, recommendations)
            self._create_notifications(oid, recommendations)

        return recommendations

    # -----------------------------------------------------------------
    # Not bazlı öneriler
    # -----------------------------------------------------------------

    def _grade_based_recommendations(self, student_id: ObjectId) -> List[Dict]:
        recs = []
        pipeline = [
            {"$match": {"student_id": student_id}},
            {"$lookup": {"from": "courses", "localField": "course_id", "foreignField": "_id", "as": "course"}},
            {"$unwind": "$course"},
        ]
        grades = list(self.db.grades.aggregate(pipeline))

        for grade in grades:
            score = grade.get("weighted_average")
            course_name = grade.get("course", {}).get("course_name", "")
            course_code = grade.get("course", {}).get("course_code", "")

            if score is None:
                continue

            if score < 50:
                recs.append(self._make_rec(
                    category=self.CATEGORY_GRADE,
                    priority=self.PRIORITY_HIGH,
                    title=f"{course_name} dersinde acil destek gerekiyor",
                    message=(
                        f"{course_name} ({course_code}) dersindeki ağırlıklı ortalamanız "
                        f"{score:.1f} puan ile başarısızlık sınırının çok altında. "
                        f"Devam etmediğiniz takdirde dersten kalma riskiniz yüksektir."
                    ),
                    action="Öğretmeninizle özel ders görüşmesi yapın ve telafi sınavı olanaklarını araştırın.",
                    course_name=course_name,
                    course_code=course_code,
                    score=score,
                ))
            elif score < 65:
                recs.append(self._make_rec(
                    category=self.CATEGORY_GRADE,
                    priority=self.PRIORITY_HIGH,
                    title=f"{course_name} dersinde ek çalışma gerekiyor",
                    message=(
                        f"{course_name} ({course_code}) dersindeki ortalamanız {score:.1f} puan. "
                        f"Bu ders için haftada en az 3 saat ek çalışma yapmanız önerilir."
                    ),
                    action="Günde en az 1 saat ek problem çözümü yapın ve soru bankalarından yararlanın.",
                    course_name=course_name,
                    course_code=course_code,
                    score=score,
                ))
            elif score < 75:
                recs.append(self._make_rec(
                    category=self.CATEGORY_GRADE,
                    priority=self.PRIORITY_MEDIUM,
                    title=f"{course_name} dersinde gelişim potansiyeli var",
                    message=(
                        f"{course_name} ({course_code}) notunuz {score:.1f}. "
                        f"Konuları tekrar gözden geçirerek 10 puan daha yükseltebilirsiniz."
                    ),
                    action="Zayıf konuları tekrar edin ve ödev/proje teslimlerinde geç kalmayın.",
                    course_name=course_name,
                    course_code=course_code,
                    score=score,
                ))

        return recs

    # -----------------------------------------------------------------
    # Devamsızlık bazlı öneriler
    # -----------------------------------------------------------------

    def _attendance_based_recommendations(self, student_id: ObjectId) -> List[Dict]:
        recs = []
        total = self.db.attendance.count_documents({"student_id": student_id})
        if total == 0:
            return recs

        absent  = self.db.attendance.count_documents({"student_id": student_id, "status": "absent"})
        late    = self.db.attendance.count_documents({"student_id": student_id, "status": "late"})
        weighted = absent + late * 0.5
        absence_rate = weighted / total * 100

        if absence_rate >= 30:
            recs.append(self._make_rec(
                category=self.CATEGORY_ATTENDANCE,
                priority=self.PRIORITY_HIGH,
                title="Devamsızlık oranı kritik seviyede (%{:.1f})".format(absence_rate),
                message=(
                    f"Toplam devamsızlık oranınız %{absence_rate:.1f} ile kritik eşiği aşmıştır. "
                    f"Bu durum akademik başarınızı ve dönem geçme durumunuzu doğrudan tehdit etmektedir. "
                    f"Bazı derslerde devamsızlık sınırını aştıysanız dersten muaf tutulabilirsiniz."
                ),
                action="Velileriniz ve danışman öğretmeninizle acilen görüşün. Devamsızlık gerekçelerinizi belgelendirin.",
                absence_rate=round(absence_rate, 1),
            ))
        elif absence_rate >= 20:
            recs.append(self._make_rec(
                category=self.CATEGORY_ATTENDANCE,
                priority=self.PRIORITY_HIGH,
                title="Ders devamlılığınızı artırmanız önerilir",
                message=(
                    f"Devamsızlık oranınız %{absence_rate:.1f}. "
                    f"Üniversitede devamsızlık sınırı genellikle %30'dur; bu sınıra yaklaşıyorsunuz."
                ),
                action="Haftada en fazla 1 gün devamsızlık hedefleyin. Zorunlu devamsızlıklarınızı raporlayın.",
                absence_rate=round(absence_rate, 1),
            ))
        elif absence_rate >= 10:
            recs.append(self._make_rec(
                category=self.CATEGORY_ATTENDANCE,
                priority=self.PRIORITY_MEDIUM,
                title="Devamsızlık oranınıza dikkat edin",
                message=f"Devamsızlık oranınız %{absence_rate:.1f}. Artmadan önlem alın.",
                action="Derslere düzenli katılımı sürdürün.",
                absence_rate=round(absence_rate, 1),
            ))

        if late >= 5:
            recs.append(self._make_rec(
                category=self.CATEGORY_ATTENDANCE,
                priority=self.PRIORITY_MEDIUM,
                title="Geç kalma sıklığı fazla",
                message=(
                    f"Bu dönem {late} kez geç kaldınız. "
                    f"Geç kalınan dersler yarım devamsızlık olarak sayılmaktadır."
                ),
                action="Ders saatinden en az 10 dakika önce sınıfta olun. Toplu taşıma saatlerini gözden geçirin.",
            ))

        return recs

    # -----------------------------------------------------------------
    # Aktivite bazlı öneriler
    # -----------------------------------------------------------------

    def _activity_based_recommendations(self, student_id: ObjectId) -> List[Dict]:
        recs = []
        activities  = list(self.db.activities.find({"student_id": student_id, "is_active": True}))
        total_hours = sum(a.get("weekly_hours", 0) for a in activities)
        has_sport   = any(a.get("activity_type") == "sport" for a in activities)

        if not activities:
            recs.append(self._make_rec(
                category=self.CATEGORY_ACTIVITY,
                priority=self.PRIORITY_MEDIUM,
                title="Sosyal aktivitelere katılmanız önerilir",
                message=(
                    "Hiç kulüp veya aktiviteye kayıtlı değilsiniz. "
                    "Araştırmalar, sosyal aktivitelerin akademik motivasyonu ve "
                    "problem çözme becerilerini geliştirdiğini göstermektedir."
                ),
                action="Bölümünüzün kulüplerini araştırın. Kodlama Kulübü veya Robotik Takımı başlangıç için idealdir.",
            ))
        elif total_hours > 20:
            recs.append(self._make_rec(
                category=self.CATEGORY_ACTIVITY,
                priority=self.PRIORITY_MEDIUM,
                title="Aktivite yoğunluğu akademik çalışmayı olumsuz etkileyebilir",
                message=(
                    f"Haftalık {total_hours:.1f} saat aktivite yapıyorsunuz. "
                    f"Akademik çalışma için haftada en az 20 saat ayırmanız gerektiğini unutmayın."
                ),
                action="Aktivite ve ders çalışma dengesini gözden geçirin. Bir veya iki aktiviteden ayrılmayı değerlendirin.",
            ))

        if not has_sport:
            recs.append(self._make_rec(
                category=self.CATEGORY_ACTIVITY,
                priority=self.PRIORITY_LOW,
                title="Düzenli spor aktivitesi ekleyebilirsiniz",
                message=(
                    "Düzenli fiziksel aktivite zihinsel yorgunluğu azaltır, "
                    "odaklanmayı güçlendirir ve ders verimliliğini artırır."
                ),
                action="Haftada 2-3 kez 30 dakika yürüyüş veya okul spor kulübüne katılımı deneyin.",
            ))

        return recs

    # -----------------------------------------------------------------
    # Performans trendi önerileri
    # -----------------------------------------------------------------

    def _performance_trend_recommendations(self, student_id: ObjectId) -> List[Dict]:
        recs = []
        analyses = list(
            self.db.performance_analysis.find({"student_id": student_id})
            .sort("analysis_date", -1)
            .limit(3)
        )

        if len(analyses) >= 2:
            latest_avg = analyses[0].get("data", {}).get("grade_analysis", {}).get("overall_average", 0)
            prev_avg   = analyses[1].get("data", {}).get("grade_analysis", {}).get("overall_average", 0)

            if prev_avg > 0 and latest_avg < prev_avg - 5:
                recs.append(self._make_rec(
                    category=self.CATEGORY_PERFORMANCE,
                    priority=self.PRIORITY_HIGH,
                    title="Performansınızda düşüş tespit edildi",
                    message=(
                        f"Ortalama notunuz bir önceki analize göre {prev_avg - latest_avg:.1f} puan düştü "
                        f"({prev_avg:.1f} → {latest_avg:.1f}). "
                        f"Bu düşüşün nedenlerini hızla analiz etmeniz önerilir."
                    ),
                    action="Rehber öğretmeninizle veya bölüm danışmanınızla görüşün. Çalışma rutininizi gözden geçirin.",
                    trend="Düşen",
                    change=round(latest_avg - prev_avg, 1),
                ))
            elif prev_avg > 0 and latest_avg > prev_avg + 5:
                recs.append(self._make_rec(
                    category=self.CATEGORY_PERFORMANCE,
                    priority=self.PRIORITY_LOW,
                    title="Performansınız yükseliyor — tebrikler!",
                    message=(
                        f"Ortalama notunuz {latest_avg - prev_avg:.1f} puan arttı "
                        f"({prev_avg:.1f} → {latest_avg:.1f}). Bu başarıyı sürdürün."
                    ),
                    action="Mevcut çalışma yönteminizi ve rutininizi koruyun.",
                    trend="Yükselen",
                    change=round(latest_avg - prev_avg, 1),
                ))

        return recs

    # -----------------------------------------------------------------
    # Ders bazlı çalışma planı önerileri
    # -----------------------------------------------------------------

    def _study_plan_recommendations(self, student_id: ObjectId) -> List[Dict]:
        recs = []
        pipeline = [
            {"$match": {"student_id": student_id}},
            {"$lookup": {"from": "courses", "localField": "course_id", "foreignField": "_id", "as": "course"}},
            {"$unwind": "$course"},
        ]
        grades = list(self.db.grades.aggregate(pipeline))

        weak = [
            (g["course"].get("course_name", ""), g["course"].get("course_code", ""), g.get("weighted_average", 0))
            for g in grades
            if g.get("weighted_average") is not None and g["weighted_average"] < 70
        ]

        if not weak:
            return recs

        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"]
        plan_lines = []
        for idx, (cname, ccode, score) in enumerate(weak):
            hours = 2.0 if score < 50 else 1.5
            day   = days[idx % len(days)]
            plan_lines.append(f"• {day}: {cname} ({ccode}) — {hours} saat")

        plan_text = "\n".join(plan_lines)

        recs.append(self._make_rec(
            category=self.CATEGORY_STUDY_PLAN,
            priority=self.PRIORITY_HIGH if any(s < 60 for _, _, s in weak) else self.PRIORITY_MEDIUM,
            title="Ders Bazlı Çalışma Planı",
            message=(
                f"Düşük notlu {len(weak)} derse yönelik haftalık çalışma planı önerilmektedir:\n\n"
                f"{plan_text}\n\n"
                f"Her oturumu 25 dakika çalışma + 5 dakika mola (Pomodoro tekniği) şeklinde uygulayın."
            ),
            action="Bu planı ajandanıza/takviminize ekleyin ve her hafta başında güncelleyin.",
            weak_courses=[{"name": n, "code": c, "score": s} for n, c, s in weak],
        ))

        return recs

    # -----------------------------------------------------------------
    # Zaman yönetimi önerileri
    # -----------------------------------------------------------------

    def _time_management_recommendations(self, student_id: ObjectId) -> List[Dict]:
        recs = []

        total_att = self.db.attendance.count_documents({"student_id": student_id})
        absent    = self.db.attendance.count_documents({"student_id": student_id, "status": "absent"})
        activities = list(self.db.activities.find({"student_id": student_id, "is_active": True}))
        weekly_hours = sum(a.get("weekly_hours", 0) for a in activities)

        absence_rate = (absent / total_att * 100) if total_att > 0 else 0
        overloaded   = weekly_hours > 15
        high_absence = absence_rate > 15

        if not overloaded and not high_absence:
            return recs

        tips = [
            "✦ Haftalık ders programınızı Pazar akşamı planlayın.",
            "✦ Her gün 30 dakika ertesi günü planlayın (günlük liste).",
            "✦ Dersleri öncelik sırasına göre sıralayın: kritik → orta → kolay.",
            "✦ Telefon bildirimlerini ders saatlerinde kapatın.",
        ]
        if overloaded:
            tips.append(f"✦ Haftalık {weekly_hours:.0f} saatlik aktivite yüküyle ders çalışma süreniz kısıtlı. Bir aktiviteyi bırakmayı düşünün.")
        if high_absence:
            tips.append(f"✦ %{absence_rate:.1f} devamsızlık oranınızla dersleri telafi etmek için ekstra zaman ayırmanız gerekiyor.")

        recs.append(self._make_rec(
            category=self.CATEGORY_TIME_MGMT,
            priority=self.PRIORITY_MEDIUM,
            title="Zaman Yönetimi Önerileri",
            message="\n".join(tips),
            action="Bu önerileri önümüzdeki hafta uygulamaya başlayın ve 2 hafta sonra değerlendirin.",
            weekly_activity_hours=weekly_hours,
            absence_rate=round(absence_rate, 1),
        ))

        return recs

    # -----------------------------------------------------------------
    # Bildirim üretme
    # -----------------------------------------------------------------

    def _create_notifications(self, student_id: ObjectId, recommendations: List[Dict]):
        """Yüksek öncelikli önerilerden otomatik bildirim kayıtları oluşturur."""
        CATEGORY_TO_TYPE = {
            self.CATEGORY_GRADE:       "low_grade_risk",
            self.CATEGORY_ATTENDANCE:  "attendance_warning",
            self.CATEGORY_PERFORMANCE: "performance_drop",
            self.CATEGORY_STUDY_PLAN:  "study_plan",
            self.CATEGORY_TIME_MGMT:   "time_management",
        }

        notifications = []
        for rec in recommendations:
            if rec.get("priority") not in (self.PRIORITY_HIGH, self.PRIORITY_MEDIUM):
                continue
            ntype = CATEGORY_TO_TYPE.get(rec.get("category"), "general")
            notifications.append({
                "student_id":        student_id,
                "notification_type": ntype,
                "title":             rec.get("title", ""),
                "message":           rec.get("message", "")[:300],
                "priority":          rec.get("priority"),
                "related_course":    rec.get("course_name"),
                "is_read":           False,
                "created_at":        datetime.utcnow(),
            })

        if notifications:
            self.db.notifications.insert_many(notifications)

    # -----------------------------------------------------------------
    # Yardımcı metodlar
    # -----------------------------------------------------------------

    @staticmethod
    def _make_rec(category: str, priority: str, title: str, message: str,
                  action: str = "", **extra) -> Dict:
        rec = {
            "category": category,
            "priority": priority,
            "title":    title,
            "message":  message,
            "action":   action,
            "created_at": datetime.utcnow().isoformat(),
        }
        rec.update(extra)
        return rec

    def _save_recommendations(self, student_id: ObjectId, recommendations: List[Dict]):
        self.db.recommendations.insert_one({
            "student_id":      student_id,
            "recommendations": recommendations,
            "created_at":      datetime.utcnow(),
        })

    def get_latest_recommendations(self, student_id: str) -> List[Dict]:
        doc = self.db.recommendations.find_one(
            {"student_id": ObjectId(student_id)},
            sort=[("created_at", -1)],
        )
        return doc.get("recommendations", []) if doc else []

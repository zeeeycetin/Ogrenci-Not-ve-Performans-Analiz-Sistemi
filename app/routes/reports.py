"""
PDF Rapor Route'ları
"""
from flask import Blueprint, current_app, session, send_file, abort
from bson import ObjectId
from io import BytesIO
from app.utils.auth import login_required, teacher_required
from app.utils.helpers import serialize_doc
from app.analysis.analytics_engine import PerformanceAnalyzer
from app.recommendations.recommendation_engine import RecommendationEngine
from app.reports.pdf_generator import generate_student_pdf, generate_class_pdf

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/student/<student_id>")
@login_required
def student_report(student_id: str):
    """Öğrenci performans raporunu PDF olarak döndürür."""
    try:
        oid = ObjectId(student_id)
    except Exception:
        abort(400)

    student = current_app.db.students.find_one({"_id": oid})
    if not student:
        abort(404)

    # Yetki kontrolü: öğrenci yalnızca kendi raporunu indirebilir
    user = session.get("user", {})
    if user.get("role") == "student":
        uid = ObjectId(user["id"])
        own = current_app.db.students.find_one({"user_id": uid, "_id": oid})
        if not own:
            abort(403)

    # Analiz üret / en son analizi kullan
    analyzer = PerformanceAnalyzer(current_app.db)
    analysis = analyzer.analyze_student(student_id)
    if "error" in analysis:
        analysis = {}

    # Öneriler
    recommender = RecommendationEngine(current_app.db)
    recommendations = recommender.get_latest_recommendations(student_id)

    student_data = serialize_doc(student)
    pdf_bytes = generate_student_pdf(student_data, analysis, recommendations)

    name_safe = student_data.get("full_name", "ogrenci").replace(" ", "_")
    filename   = f"Performans_Raporu_{name_safe}.pdf"

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@reports_bp.route("/class/<class_name>")
@teacher_required
def class_report(class_name: str):
    """Sınıf raporunu PDF olarak döndürür."""
    analyzer = PerformanceAnalyzer(current_app.db)
    analysis = analyzer.analyze_class(class_name)
    if "error" in analysis:
        abort(404)

    students = serialize_doc(list(
        current_app.db.students.find({"class_name": class_name}).sort("full_name", 1)
    ))

    pdf_bytes = generate_class_pdf(class_name, analysis, students)
    filename  = f"Sinif_Raporu_{class_name.replace(' ','_')}.pdf"

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )

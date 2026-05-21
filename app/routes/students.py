from flask import Blueprint, request, current_app, render_template, session
from app.services.student_service import StudentService
from app.utils.auth import teacher_required, login_required, get_current_user_id, get_current_role
from app.utils.helpers import success_response, error_response, to_object_id

students_bp = Blueprint("students", __name__)


def get_service():
    return StudentService(current_app.db)


# -----------------------------------------------------------------
# Öğrenci listesi
# -----------------------------------------------------------------

@students_bp.route("/", methods=["GET"])
@login_required
def list_students():
    class_name = request.args.get("class_name")
    sort_by = request.args.get("sort_by", "full_name")
    order = int(request.args.get("order", 1))
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    result = get_service().get_all_students(class_name, sort_by, order, page, per_page)

    if request.is_json:
        return success_response(result)
    return render_template("students/list.html", **result, classes=get_service().get_class_list())


# -----------------------------------------------------------------
# Öğrenci detayı
# -----------------------------------------------------------------

@students_bp.route("/<student_id>", methods=["GET"])
@login_required
def get_student(student_id: str):
    student = get_service().get_student_by_id(student_id)
    if not student:
        return error_response("Öğrenci bulunamadı.", 404)

    summary = get_service().get_student_summary(student_id)

    if request.is_json:
        return success_response({"student": student, "summary": summary})
    return render_template("students/detail.html", student=student, summary=summary)


# -----------------------------------------------------------------
# Öğrenci oluştur
# -----------------------------------------------------------------

@students_bp.route("/", methods=["POST"])
@teacher_required
def create_student():
    data = request.get_json() or request.form.to_dict()
    result = get_service().create_student(data)
    if not result["success"]:
        return error_response(result["message"], 409)
    return success_response({"student_id": result["student_id"]}, "Öğrenci oluşturuldu.", 201)


# -----------------------------------------------------------------
# Öğrenci güncelle
# -----------------------------------------------------------------

@students_bp.route("/<student_id>", methods=["PUT", "PATCH"])
@teacher_required
def update_student(student_id: str):
    data = request.get_json() or request.form.to_dict()
    result = get_service().update_student(student_id, data)
    if not result["success"]:
        return error_response(result["message"], 404)
    return success_response(message=result["message"])


# -----------------------------------------------------------------
# Öğrenci sil
# -----------------------------------------------------------------

@students_bp.route("/<student_id>", methods=["DELETE"])
@teacher_required
def delete_student(student_id: str):
    result = get_service().delete_student(student_id)
    if not result["success"]:
        return error_response(result["message"], 404)
    return success_response(message=result["message"])

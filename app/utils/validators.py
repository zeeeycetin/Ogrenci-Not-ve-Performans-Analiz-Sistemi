import re
from typing import Tuple, Dict


def validate_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password: str, strict: bool = False) -> Tuple[bool, str]:
    if len(password) < 6:
        return False, "Şifre en az 6 karakter olmalıdır."
    if strict:
        if not re.search(r"[A-Z]", password):
            return False, "Şifre en az bir büyük harf içermelidir."
        if not re.search(r"[0-9]", password):
            return False, "Şifre en az bir rakam içermelidir."
    return True, ""


def validate_score(score) -> Tuple[bool, str]:
    try:
        val = float(score)
        if not (0 <= val <= 100):
            return False, "Not 0-100 arasında olmalıdır."
        return True, ""
    except (TypeError, ValueError):
        return False, "Geçersiz not formatı."


def validate_register_data(data: dict, strict_password: bool = True) -> Dict[str, str]:
    errors = {}
    if not data.get("username"):
        errors["username"] = "Kullanıcı adı zorunludur."
    if not data.get("email") or not validate_email(data["email"]):
        errors["email"] = "Geçerli bir e-posta adresi giriniz."
    if not data.get("full_name"):
        errors["full_name"] = "Ad Soyad zorunludur."
    if not data.get("role") or data["role"] not in ("teacher", "student", "admin"):
        errors["role"] = "Geçerli bir rol seçiniz (teacher/student/admin)."
    ok, msg = validate_password(data.get("password", ""), strict=strict_password)
    if not ok:
        errors["password"] = msg
    return errors


def validate_grade_data(data: dict) -> Dict[str, str]:
    errors = {}
    for field in ("midterm_score", "final_score"):
        if data.get(field) is not None:
            ok, msg = validate_score(data[field])
            if not ok:
                errors[field] = msg
    return errors

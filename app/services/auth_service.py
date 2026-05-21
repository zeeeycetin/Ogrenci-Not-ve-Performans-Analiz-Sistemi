from datetime import datetime
from bson import ObjectId
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_bcrypt import generate_password_hash, check_password_hash
from app.models.user import User
from app.utils.validators import validate_register_data


class AuthService:
    def __init__(self, db):
        self.db = db

    # -----------------------------------------------------------------
    # Kayıt
    # -----------------------------------------------------------------

    def register(self, data: dict, strict_password: bool = True) -> dict:
        errors = validate_register_data(data, strict_password=strict_password)
        if errors:
            return {"success": False, "errors": errors}

        if self.db.users.find_one({"email": data["email"].lower()}):
            return {"success": False, "errors": {"email": "Bu e-posta zaten kayıtlı."}}

        if self.db.users.find_one({"username": data["username"]}):
            return {"success": False, "errors": {"username": "Bu kullanıcı adı zaten alınmış."}}

        is_approved = data.get("is_approved", None)
        if is_approved is True or str(is_approved) == "True":
            is_approved = True
        user = User(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            role=data["role"],
            full_name=data["full_name"],
            is_approved=is_approved,
        )
        self.db.users.insert_one(user.to_dict())
        self._create_profile(user, data)
        return {"success": True, "user_id": str(user._id), "role": user.role}

    def _create_profile(self, user, data: dict):
        """Kayıt sırasında rol bazlı profil otomatik oluşturur."""
        now = datetime.utcnow()
        if user.role == "teacher":
            if not self.db.teachers.find_one({"user_id": user._id}):
                self.db.teachers.insert_one({
                    "user_id": user._id,
                    "teacher_number": data.get("teacher_number") or f"T{str(user._id)[-5:].upper()}",
                    "full_name": user.full_name,
                    "branch": data.get("branch", "Belirtilmedi"),
                    "phone": data.get("phone", ""),
                    "profile_image": "",
                    "assigned_classes": [],
                    "created_at": now,
                    "updated_at": now,
                })
        elif user.role == "student":
            if not self.db.students.find_one({"user_id": user._id}):
                self.db.students.insert_one({
                    "user_id": user._id,
                    "student_number": data.get("student_number") or f"S{str(user._id)[-6:].upper()}",
                    "full_name": user.full_name,
                    "class_name": data.get("class_name", "Belirtilmedi"),
                    "birth_date": None,
                    "gender": data.get("gender", ""),
                    "phone": data.get("phone", ""),
                    "address": "",
                    "profile_image": "",
                    "created_at": now,
                    "updated_at": now,
                })

    # -----------------------------------------------------------------
    # Giriş
    # -----------------------------------------------------------------

    def login(self, identifier: str, password: str) -> dict:
        # Önce users koleksiyonuna bak (eski öğretmenler, öğrenciler, adminler)
        user_doc = self.db.users.find_one({
            "$or": [
                {"email": identifier.lower()},
                {"username": identifier},
            ]
        })

        if user_doc:
            if not check_password_hash(user_doc["password_hash"], password):
                return {"success": False, "message": "Şifre yanlış."}

            if not user_doc.get("is_active", True):
                return {"success": False, "message": "Hesap devre dışı."}

            is_approved = user_doc.get("is_approved")
            if is_approved is False:
                return {"success": False, "message": "pending_approval"}

            additional_claims = {"role": user_doc["role"], "full_name": user_doc["full_name"]}
            access_token = create_access_token(
                identity=str(user_doc["_id"]),
                additional_claims=additional_claims,
            )
            refresh_token = create_refresh_token(identity=str(user_doc["_id"]))
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": str(user_doc["_id"]),
                    "username": user_doc["username"],
                    "email": user_doc["email"],
                    "role": user_doc["role"],
                    "full_name": user_doc["full_name"],
                },
            }

        # Yeni şema öğretmenleri: email + password_hash doğrudan teachers koleksiyonunda
        teacher_doc = self.db.teachers.find_one({
            "email": identifier.lower(),
            "password_hash": {"$exists": True},
        })
        if not teacher_doc:
            return {"success": False, "message": "Kullanıcı bulunamadı."}

        if not check_password_hash(teacher_doc["password_hash"], password):
            return {"success": False, "message": "Şifre yanlış."}

        role = teacher_doc.get("role", "teacher")
        full_name = teacher_doc.get("name") or teacher_doc.get("full_name", "")
        additional_claims = {"role": role, "full_name": full_name}
        access_token = create_access_token(
            identity=str(teacher_doc["_id"]),
            additional_claims=additional_claims,
        )
        refresh_token = create_refresh_token(identity=str(teacher_doc["_id"]))

        self.db.teachers.update_one(
            {"_id": teacher_doc["_id"]},
            {"$set": {"last_login": datetime.utcnow()}},
        )

        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": str(teacher_doc["_id"]),
                "username": teacher_doc.get("teacher_id", ""),
                "email": teacher_doc["email"],
                "role": role,
                "full_name": full_name,
            },
        }

    # -----------------------------------------------------------------
    # Şifre değiştir
    # -----------------------------------------------------------------

    def change_password(self, user_id: str, old_password: str, new_password: str) -> dict:
        user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            return {"success": False, "message": "Kullanıcı bulunamadı."}

        if not check_password_hash(user_doc["password_hash"], old_password):
            return {"success": False, "message": "Mevcut şifre yanlış."}

        new_hash = generate_password_hash(new_password).decode("utf-8")
        self.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": new_hash, "updated_at": datetime.utcnow()}},
        )
        return {"success": True, "message": "Şifre güncellendi."}

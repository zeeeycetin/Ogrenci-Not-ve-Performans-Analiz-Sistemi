from datetime import datetime
from bson import ObjectId
from flask_bcrypt import generate_password_hash, check_password_hash


class User:
    ROLE_TEACHER = "teacher"
    ROLE_STUDENT = "student"
    ROLE_ADMIN   = "admin"

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        role: str,
        full_name: str,
        _id=None,
        is_active: bool = True,
        is_approved: bool = None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        self._id = _id or ObjectId()
        self.username = username
        self.email = email.lower().strip()
        self.password_hash = generate_password_hash(password).decode("utf-8")
        self.role = role
        self.full_name = full_name
        self.is_active = is_active
        # Admin otomatik onaylı, diğerleri onay bekler
        self.is_approved = is_approved if is_approved is not None else (role == "admin")
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_approved": self.is_approved,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_public_dict(self) -> dict:
        return {
            "id": str(self._id),
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "full_name": self.full_name,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        obj = cls.__new__(cls)
        obj._id = data.get("_id", ObjectId())
        obj.username = data["username"]
        obj.email = data["email"]
        obj.password_hash = data["password_hash"]
        obj.role = data["role"]
        obj.full_name = data["full_name"]
        obj.is_active = data.get("is_active", True)
        obj.created_at = data.get("created_at", datetime.utcnow())
        obj.updated_at = data.get("updated_at", datetime.utcnow())
        return obj

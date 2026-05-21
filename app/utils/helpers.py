from bson import ObjectId
from datetime import datetime
from typing import Any
import json
import re


def serialize_doc(doc: Any) -> Any:
    """MongoDB dökümanlarındaki ObjectId ve datetime alanlarını JSON-uyumlu hale getirir."""
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        result = {k: serialize_doc(v) for k, v in doc.items()}
        if "_id" in result and "id" not in result:
            result["id"] = result["_id"]
        return result
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return doc.isoformat()
    return doc


def paginate_cursor(cursor, page: int = 1, per_page: int = 20) -> dict:
    total = cursor.count()
    items = list(cursor.skip((page - 1) * per_page).limit(per_page))
    return {
        "items": serialize_doc(items),
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


def success_response(data: Any = None, message: str = "Başarılı", status_code: int = 200):
    from flask import jsonify
    resp = {"success": True, "message": message}
    if data is not None:
        resp["data"] = data
    return jsonify(resp), status_code


def error_response(message: str = "Hata", status_code: int = 400, errors: dict = None):
    from flask import jsonify
    resp = {"success": False, "message": message}
    if errors:
        resp["errors"] = errors
    return jsonify(resp), status_code


def validate_object_id(oid: str) -> bool:
    return ObjectId.is_valid(oid)


def to_object_id(oid: str) -> ObjectId:
    if not validate_object_id(oid):
        raise ValueError(f"Geçersiz ObjectId: {oid}")
    return ObjectId(oid)


def calculate_percentage(part: float, total: float) -> float:
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

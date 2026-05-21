"""
Admin kullanicisini dogrudan MongoDB Atlas'a ekler.
Kullanim: python add_admin_direct.py
"""
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from flask_bcrypt import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = os.getenv("DB_NAME", "ogrenci_sistemi")

ADMIN_USERNAME = "admin"
ADMIN_EMAIL    = "admin@edutrack.com"
ADMIN_PASSWORD = "Admin123"
ADMIN_NAME     = "Sistem Yöneticisi"

client = MongoClient(MONGO_URI)
db     = client[DB_NAME]

existing = db.users.find_one({"username": ADMIN_USERNAME})
if existing:
    print(f"[!] '{ADMIN_USERNAME}' zaten mevcut. İşlem yapılmadı.")
else:
    password_hash = generate_password_hash(ADMIN_PASSWORD).decode("utf-8")
    now = datetime.utcnow()
    doc = {
        "_id":           ObjectId(),
        "username":      ADMIN_USERNAME,
        "email":         ADMIN_EMAIL,
        "password_hash": password_hash,
        "role":          "admin",
        "full_name":     ADMIN_NAME,
        "is_active":     True,
        "is_approved":   True,
        "created_at":    now,
        "updated_at":    now,
    }
    db.users.insert_one(doc)
    print("=" * 50)
    print("Yönetici hesabı oluşturuldu!")
    print(f"  Kullanıcı adı : {ADMIN_USERNAME}")
    print(f"  E-posta       : {ADMIN_EMAIL}")
    print(f"  Şifre         : {ADMIN_PASSWORD}")
    print("=" * 50)

client.close()

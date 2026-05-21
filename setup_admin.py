"""
Varsayılan yönetici hesabı oluşturur.
Kullanım: python setup_admin.py
"""
from app import create_app
from app.services.auth_service import AuthService

ADMIN_USERNAME = "admin"
ADMIN_EMAIL    = "admin@edutrack.com"
ADMIN_PASSWORD = "Admin123"
ADMIN_NAME     = "Sistem Yöneticisi"

app = create_app()

with app.app_context():
    db = app.db
    existing = db.users.find_one({"username": ADMIN_USERNAME})
    if existing:
        print(f"[!] '{ADMIN_USERNAME}' kullanıcısı zaten mevcut. İşlem yapılmadı.")
    else:
        result = AuthService(db).register({
            "username":    ADMIN_USERNAME,
            "email":       ADMIN_EMAIL,
            "password":    ADMIN_PASSWORD,
            "role":        "admin",
            "full_name":   ADMIN_NAME,
            "is_approved": True,
        })
        if result["success"]:
            print("=" * 50)
            print("Yönetici hesabı oluşturuldu!")
            print(f"  Kullanıcı adı : {ADMIN_USERNAME}")
            print(f"  E-posta       : {ADMIN_EMAIL}")
            print(f"  Şifre         : {ADMIN_PASSWORD}")
            print("=" * 50)
        else:
            print("[X] Hata:", result)

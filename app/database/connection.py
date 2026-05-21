import ssl
import certifi
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi
import pymongo.ssl_support as _pymongo_ssl_support

logger = logging.getLogger(__name__)

_client: MongoClient = None
_db = None

# Python 3.14 + OpenSSL 3.0: pymongo'nun get_ssl_context fonksiyonunu yamala,
# cipher güvenlik seviyesini düşür ve eski sunucu bağlantısına izin ver.
_orig_get_ssl_context = _pymongo_ssl_support.get_ssl_context

def _patched_get_ssl_context(*args, **kwargs):
    ctx = _orig_get_ssl_context(*args, **kwargs)
    try:
        ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
    except Exception:
        pass
    if hasattr(ssl, "OP_LEGACY_SERVER_CONNECT"):
        ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
    return ctx

_pymongo_ssl_support.get_ssl_context = _patched_get_ssl_context


def get_client(mongo_uri: str) -> MongoClient:
    global _client
    if _client is None:
        is_atlas = "mongodb+srv://" in mongo_uri or "mongodb.net" in mongo_uri
        kwargs = {
            "serverSelectionTimeoutMS": 15000,
            "connectTimeoutMS": 15000,
            "socketTimeoutMS": 30000,
        }
        if is_atlas:
            kwargs["server_api"] = ServerApi("1")
            kwargs["tls"] = True
            kwargs["tlsInsecure"] = True
        _client = MongoClient(mongo_uri, **kwargs)
    return _client


def get_db(mongo_uri: str, db_name: str):
    """
    Lazy MongoDB bağlantısı — uygulama başlarken değil,
    ilk veritabanı erişiminde bağlanır.
    """
    global _db
    if _db is None:
        client = get_client(mongo_uri)
        _db = client[db_name]
        # Indexleri arka planda oluştur (hata olursa sessizce geç)
        try:
            _create_indexes(_db)
            logger.info("MongoDB bağlantısı ve indexler hazır.")
        except Exception as e:
            logger.warning(f"MongoDB index oluşturulamadı (henüz bağlı olmayabilir): {e}")
    return _db


def _create_indexes(db):
    # users koleksiyonu
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("username", ASCENDING)], unique=True)
    db.users.create_index([("role", ASCENDING)])

    # students koleksiyonu
    db.students.create_index([("student_number", ASCENDING)], unique=True)
    db.students.create_index([("user_id", ASCENDING)])
    db.students.create_index([("class_name", ASCENDING)])

    # teachers koleksiyonu
    db.teachers.create_index([("user_id", ASCENDING)], unique=True)
    db.teachers.create_index([("teacher_number", ASCENDING)], unique=True)

    # courses koleksiyonu
    db.courses.create_index([("course_code", ASCENDING)], unique=True)
    db.courses.create_index([("teacher_id", ASCENDING)])

    # grades koleksiyonu
    db.grades.create_index([("student_id", ASCENDING), ("course_id", ASCENDING)])
    db.grades.create_index([("student_id", ASCENDING)])
    db.grades.create_index([("course_id", ASCENDING)])

    # attendance koleksiyonu
    db.attendance.create_index([("student_id", ASCENDING), ("course_id", ASCENDING), ("date", DESCENDING)])
    db.attendance.create_index([("student_id", ASCENDING)])

    # activities koleksiyonu
    db.activities.create_index([("student_id", ASCENDING)])

    # recommendations koleksiyonu
    db.recommendations.create_index([("student_id", ASCENDING), ("created_at", DESCENDING)])

    # performance_analysis koleksiyonu
    db.performance_analysis.create_index([("student_id", ASCENDING), ("analysis_date", DESCENDING)])

    # login_logs koleksiyonu
    db.login_logs.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])

    logger.info("MongoDB indexleri oluşturuldu.")


def close_connection():
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB bağlantısı kapatıldı.")

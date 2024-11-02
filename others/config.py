from db_config import get_db_connection
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_por_defecto_segura')
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'

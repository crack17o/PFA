import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://user:password@localhost/unimate')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SESSION_TYPE = 'sqlalchemy'
    # SESSION_SQLALCHEMY doit être assigné dynamiquement dans create_app (voir app/__init__.py)
    PERMANENT_SESSION_LIFETIME = 3600  # 1 heure en secondes
    SESSION_COOKIE_SECURE = True  # Important pour HTTPS (Render)
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_DOMAIN = "pfa-mxrh.onrender.com"

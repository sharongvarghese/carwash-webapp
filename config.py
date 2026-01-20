import os

class Config:
    # =========================
    # SECURITY
    # =========================
    SECRET_KEY = os.getenv("SECRET_KEY", "render-secret-key")

    # =========================
    # DATABASE
    # =========================
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///carwash.db")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://", "postgresql://", 1
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # CSRF PROTECTION
    # =========================
    WTF_CSRF_ENABLED = True

    # =========================
    # EMAIL (Flask-Mail)
    # =========================
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

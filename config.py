import os

class Config:
    # SECURITY
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-change-me")

    # DATABASE
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///carwash.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CSRF
    WTF_CSRF_ENABLED = True

    # EMAIL (Flask-Mail)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
